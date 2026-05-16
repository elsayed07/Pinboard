from django.db.models import QuerySet

from apps.accounts.models import User
from apps.images.models import Image, ImagePrivacy, ImageStatus


class ImageSelector:
    @staticmethod
    def public_feed(*, page: int = 1, page_size: int = 24) -> QuerySet[Image]:
        return (
            Image.objects.filter(status=ImageStatus.READY, privacy=ImagePrivacy.PUBLIC)
            .select_related("owner", "owner__profile")
            .prefetch_related("tags")
            .order_by("-created_at")
        )

    @staticmethod
    def following_feed(*, user: User) -> QuerySet[Image]:
        following_ids = user.following.values_list("following_id", flat=True)
        return (
            Image.objects.filter(
                owner_id__in=following_ids,
                status=ImageStatus.READY,
            )
            .exclude(privacy=ImagePrivacy.PRIVATE)
            .select_related("owner", "owner__profile")
            .prefetch_related("tags")
            .order_by("-created_at")
        )

    @staticmethod
    def trending(*, limit: int = 24) -> QuerySet[Image]:
        return (
            Image.objects.filter(status=ImageStatus.READY, privacy=ImagePrivacy.PUBLIC)
            .select_related("owner", "owner__profile")
            .order_by("-like_count", "-view_count")[:limit]
        )

    @staticmethod
    def user_images(*, owner: User, viewer: User | None = None) -> QuerySet[Image]:
        qs = Image.objects.filter(owner=owner, status=ImageStatus.READY)
        if viewer is None or viewer.id != owner.id:
            qs = qs.filter(privacy=ImagePrivacy.PUBLIC)
        return qs.select_related("owner", "owner__profile").prefetch_related("tags")

    @staticmethod
    def get_detail(*, slug: str) -> Image:
        return (
            Image.objects.select_related("owner", "owner__profile", "collection")
            .prefetch_related("tags")
            .get(slug=slug, status=ImageStatus.READY)
        )
