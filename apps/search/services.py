from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import QuerySet

from apps.images.models import Image, ImagePrivacy, ImageStatus


class SearchService:
    @staticmethod
    def search_images(query: str, *, limit: int = 24) -> QuerySet[Image]:
        search_query = SearchQuery(query, search_type="websearch")
        vector = SearchVector("title", weight="A") + SearchVector("description", weight="B")
        return (
            Image.objects.filter(status=ImageStatus.READY, privacy=ImagePrivacy.PUBLIC)
            .annotate(rank=SearchRank(vector, search_query))
            .filter(rank__gte=0.1)
            .select_related("owner", "owner__profile")
            .order_by("-rank")[:limit]
        )

    @staticmethod
    def search_by_tag(tag_slug: str, *, limit: int = 24) -> QuerySet[Image]:
        return (
            Image.objects.filter(
                tags__slug=tag_slug,
                status=ImageStatus.READY,
                privacy=ImagePrivacy.PUBLIC,
            )
            .select_related("owner", "owner__profile")
            .order_by("-like_count")[:limit]
        )
