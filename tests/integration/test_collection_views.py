import pytest
from django.urls import reverse

from apps.images.models import Collection, Image
from tests.factories.accounts import UserFactory
from tests.factories.images import CollectionFactory, ImageFactory


@pytest.mark.django_db
class TestCollectionsView:
    def test_requires_login(self, client):
        resp = client.get(reverse("collections"))
        assert resp.status_code == 302
        assert "/login/" in resp["Location"]

    def test_lists_own_collections(self, client):
        user = UserFactory()
        CollectionFactory.create_batch(3, owner=user)
        CollectionFactory()  # other user's collection
        client.force_login(user)

        resp = client.get(reverse("collections"))

        assert resp.status_code == 200
        assert resp.context["collections"].count() == 3

    def test_post_creates_collection(self, client):
        user = UserFactory()
        client.force_login(user)

        resp = client.post(reverse("collections"), {"name": "My New Collection"})

        assert resp.status_code == 302
        assert Collection.objects.filter(owner=user, name="My New Collection").exists()

    def test_post_duplicate_name_shows_error(self, client):
        user = UserFactory()
        CollectionFactory(owner=user, name="Existing")
        client.force_login(user)

        resp = client.post(reverse("collections"), {"name": "Existing"})

        assert resp.status_code == 200
        assert Collection.objects.filter(owner=user, name="Existing").count() == 1


@pytest.mark.django_db
class TestCollectionDetailView:
    def test_shows_own_collection(self, client):
        user = UserFactory()
        col = CollectionFactory(owner=user)
        ImageFactory.create_batch(3, owner=user, collection=col, status="ready")
        client.force_login(user)

        resp = client.get(reverse("collection-detail", kwargs={"collection_id": str(col.id)}))

        assert resp.status_code == 200
        assert len(resp.context["images"]) == 3

    def test_cannot_view_other_users_collection(self, client):
        owner = UserFactory()
        other = UserFactory()
        col = CollectionFactory(owner=owner)
        client.force_login(other)

        resp = client.get(reverse("collection-detail", kwargs={"collection_id": str(col.id)}))

        assert resp.status_code == 404


@pytest.mark.django_db
class TestCollectionAddRemoveImage:
    def test_add_image_to_collection(self, client):
        user = UserFactory()
        col = CollectionFactory(owner=user)
        image = ImageFactory(owner=user)
        client.force_login(user)

        resp = client.post(reverse("collection-add-image", kwargs={
            "collection_id": str(col.id),
            "image_id": str(image.id),
        }))

        assert resp.status_code == 204
        image.refresh_from_db()
        assert image.collection == col

    def test_remove_image_from_collection(self, client):
        user = UserFactory()
        col = CollectionFactory(owner=user)
        image = ImageFactory(owner=user, collection=col)
        client.force_login(user)

        resp = client.post(reverse("collection-remove-image", kwargs={"image_id": str(image.id)}))

        assert resp.status_code == 204
        image.refresh_from_db()
        assert image.collection is None
