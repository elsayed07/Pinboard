from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import F, QuerySet

from apps.images.models import Image, ImagePrivacy, ImageStatus


class SearchService:
    @staticmethod
    def search_images(query: str, *, limit: int = 24) -> QuerySet[Image]:
        search_query = SearchQuery(query, search_type="websearch")

        # Use the pre-computed GIN-indexed vector when available; fall back to an
        # ad-hoc annotation for rows that have not been processed yet.
        qs = (
            Image.objects
            .filter(status=ImageStatus.READY, privacy=ImagePrivacy.PUBLIC)
            .select_related("owner", "owner__profile")
        )

        populated = qs.filter(search_vector__isnull=False)
        if populated.exists():
            return (
                populated
                .annotate(rank=SearchRank(F("search_vector"), search_query))
                .filter(rank__gte=0.05)
                .order_by("-rank")[:limit]
            )

        # Fallback: compute vector on the fly (no GIN index, but correct results)
        vector = SearchVector("title", weight="A") + SearchVector("description", weight="B")
        return (
            qs
            .annotate(rank=SearchRank(vector, search_query))
            .filter(rank__gte=0.05)
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
