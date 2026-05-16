from django.core.cache import cache
from django.db import transaction
from django.db.models import F

from apps.accounts.models import User
from apps.images.models import Image, Like, Save
from shared.cache import CacheKey
from shared.exceptions import ConflictError, NotFoundError


class EngagementService:
    @staticmethod
    @transaction.atomic
    def like(*, user: User, image_id: str) -> Like:
        try:
            image = Image.objects.get(id=image_id, status="ready")
        except Image.DoesNotExist:
            raise NotFoundError("Image not found.")

        like, created = Like.objects.get_or_create(user=user, image=image)
        if not created:
            raise ConflictError("Already liked.")

        Image.objects.filter(id=image_id).update(like_count=F("like_count") + 1)
        try:
            cache.incr(CacheKey.image_likes(image_id))
        except Exception:
            pass
        return like

    @staticmethod
    @transaction.atomic
    def unlike(*, user: User, image_id: str) -> None:
        deleted, _ = Like.objects.filter(user=user, image_id=image_id).delete()
        if not deleted:
            raise NotFoundError("Like not found.")
        Image.objects.filter(id=image_id).update(like_count=F("like_count") - 1)

    @staticmethod
    def record_view(*, image_id: str) -> int:
        key = CacheKey.image_views(image_id)
        try:
            return cache.incr(key)
        except Exception:
            cache.set(key, 1, timeout=None)
            return 1

    @staticmethod
    @transaction.atomic
    def save_image(*, user: User, image_id: str) -> Save:
        try:
            image = Image.objects.get(id=image_id, status="ready")
        except Image.DoesNotExist:
            raise NotFoundError("Image not found.")

        save, created = Save.objects.get_or_create(user=user, image=image)
        if not created:
            raise ConflictError("Already saved.")

        Image.objects.filter(id=image_id).update(save_count=F("save_count") + 1)
        return save

    @staticmethod
    def unsave_image(*, user: User, image_id: str) -> None:
        deleted, _ = Save.objects.filter(user=user, image_id=image_id).delete()
        if not deleted:
            raise NotFoundError("Save not found.")
        Image.objects.filter(id=image_id).update(save_count=F("save_count") - 1)
