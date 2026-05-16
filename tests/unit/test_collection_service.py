import pytest

from apps.images.models import Image
from apps.images.services.collections import CollectionService
from shared.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from tests.factories.accounts import UserFactory
from tests.factories.images import CollectionFactory, ImageFactory


@pytest.mark.django_db
class TestCollectionCreate:
    def test_create_returns_collection(self):
        user = UserFactory()
        col = CollectionService.create(owner=user, name="Favourites")
        assert col.owner == user
        assert col.name == "Favourites"

    def test_duplicate_name_raises_conflict(self):
        user = UserFactory()
        CollectionService.create(owner=user, name="Duplicates")
        with pytest.raises(ConflictError):
            CollectionService.create(owner=user, name="Duplicates")

    def test_different_users_can_share_name(self):
        u1, u2 = UserFactory(), UserFactory()
        CollectionService.create(owner=u1, name="Shared Name")
        col = CollectionService.create(owner=u2, name="Shared Name")
        assert col.owner == u2


@pytest.mark.django_db
class TestCollectionAddImage:
    def test_add_image_sets_collection(self):
        user = UserFactory()
        col = CollectionFactory(owner=user)
        image = ImageFactory(owner=user)

        CollectionService.add_image(user=user, collection_id=str(col.id), image_id=str(image.id))

        image.refresh_from_db()
        assert image.collection == col

    def test_add_first_image_sets_cover(self):
        user = UserFactory()
        col = CollectionFactory(owner=user, cover_image=None)
        image = ImageFactory(owner=user)

        CollectionService.add_image(user=user, collection_id=str(col.id), image_id=str(image.id))

        col.refresh_from_db()
        assert col.cover_image == image

    def test_wrong_owner_raises_not_found(self):
        owner = UserFactory()
        other = UserFactory()
        col = CollectionFactory(owner=owner)
        image = ImageFactory(owner=owner)

        with pytest.raises(NotFoundError):
            CollectionService.add_image(user=other, collection_id=str(col.id), image_id=str(image.id))

    def test_private_image_from_other_user_raises(self):
        user = UserFactory()
        other = UserFactory()
        col = CollectionFactory(owner=user)
        image = ImageFactory(owner=other, privacy="private")

        with pytest.raises(PermissionDeniedError):
            CollectionService.add_image(user=user, collection_id=str(col.id), image_id=str(image.id))


@pytest.mark.django_db
class TestCollectionRemoveImage:
    def test_remove_clears_collection_field(self):
        user = UserFactory()
        col = CollectionFactory(owner=user)
        image = ImageFactory(owner=user, collection=col)

        CollectionService.remove_image(user=user, image_id=str(image.id))

        image.refresh_from_db()
        assert image.collection is None

    def test_remove_wrong_owner_raises(self):
        owner = UserFactory()
        other = UserFactory()
        col = CollectionFactory(owner=owner)
        image = ImageFactory(owner=owner, collection=col)

        with pytest.raises(NotFoundError):
            CollectionService.remove_image(user=other, image_id=str(image.id))


@pytest.mark.django_db
class TestCollectionDelete:
    def test_delete_removes_collection(self):
        user = UserFactory()
        col = CollectionFactory(owner=user)

        CollectionService.delete(user=user, collection_id=str(col.id))

        from apps.images.models import Collection
        assert not Collection.objects.filter(id=col.id).exists()

    def test_delete_wrong_owner_raises(self):
        owner = UserFactory()
        other = UserFactory()
        col = CollectionFactory(owner=owner)

        with pytest.raises(NotFoundError):
            CollectionService.delete(user=other, collection_id=str(col.id))
