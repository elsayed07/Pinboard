from django.db import transaction

from apps.accounts.models import User
from apps.images.models import Collection, Image, ImageStatus
from shared.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from shared.utils.slugify import unique_slug


class CollectionService:
    @staticmethod
    @transaction.atomic
    def create(*, owner: User, name: str, description: str = "", is_private: bool = False) -> Collection:
        if Collection.objects.filter(owner=owner, name=name).exists():
            raise ConflictError("You already have a collection with this name.")
        return Collection.objects.create(
            owner=owner,
            name=name,
            description=description,
            is_private=is_private,
        )

    @staticmethod
    @transaction.atomic
    def add_image(*, user: User, collection_id: str, image_id: str) -> Image:
        try:
            collection = Collection.objects.get(id=collection_id, owner=user)
        except Collection.DoesNotExist:
            raise NotFoundError("Collection not found.")

        try:
            image = Image.objects.get(id=image_id, status=ImageStatus.READY)
        except Image.DoesNotExist:
            raise NotFoundError("Image not found.")

        if image.owner != user and image.privacy == "private":
            raise PermissionDeniedError()

        image.collection = collection
        image.save(update_fields=["collection", "updated_at"])

        if not collection.cover_image:
            collection.cover_image = image
            collection.save(update_fields=["cover_image", "updated_at"])

        return image

    @staticmethod
    @transaction.atomic
    def remove_image(*, user: User, image_id: str) -> None:
        updated = Image.objects.filter(
            id=image_id, owner=user
        ).update(collection=None)
        if not updated:
            raise NotFoundError("Image not found.")

    @staticmethod
    def delete(*, user: User, collection_id: str) -> None:
        deleted, _ = Collection.objects.filter(id=collection_id, owner=user).delete()
        if not deleted:
            raise NotFoundError("Collection not found.")
