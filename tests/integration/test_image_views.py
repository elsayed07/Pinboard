import pytest
from django.urls import reverse

from apps.images.models import Image, Like, Save
from tests.factories.accounts import UserFactory
from tests.factories.images import ImageFactory


@pytest.mark.django_db
class TestHomeView:
    def test_anonymous_sees_discover_template(self, client):
        ImageFactory.create_batch(3)
        resp = client.get(reverse("home"))
        assert resp.status_code == 200
        assert b"Pinboard" in resp.content

    def test_authenticated_with_no_following_falls_back_to_public(self, client):
        user = UserFactory()
        client.force_login(user)
        ImageFactory.create_batch(3)
        resp = client.get(reverse("home"))
        assert resp.status_code == 200


@pytest.mark.django_db
class TestImageDetailView:
    def test_ready_image_returns_200(self, client):
        image = ImageFactory(status="ready")
        resp = client.get(reverse("image-detail", kwargs={"slug": image.slug}))
        assert resp.status_code == 200

    def test_pending_image_returns_404(self, client):
        image = ImageFactory(status="pending")
        resp = client.get(reverse("image-detail", kwargs={"slug": image.slug}))
        assert resp.status_code == 404

    def test_increments_view_count(self, client):
        image = ImageFactory(status="ready")
        client.get(reverse("image-detail", kwargs={"slug": image.slug}))
        from django.core.cache import cache
        from shared.cache import CacheKey
        assert cache.get(CacheKey.image_views(str(image.id))) == 1


@pytest.mark.django_db
class TestLikeViews:
    def test_like_requires_login(self, client):
        image = ImageFactory()
        resp = client.post(reverse("like", kwargs={"image_id": str(image.id)}))
        assert resp.status_code == 302
        assert "/login/" in resp["Location"]

    def test_like_creates_record(self, client):
        user = UserFactory()
        image = ImageFactory()
        client.force_login(user)

        resp = client.post(reverse("like", kwargs={"image_id": str(image.id)}))

        assert resp.status_code in (200, 302)
        assert Like.objects.filter(user=user, image=image).exists()

    def test_unlike_removes_record(self, client):
        user = UserFactory()
        image = ImageFactory(like_count=1)
        Like.objects.create(user=user, image=image)
        client.force_login(user)

        resp = client.post(reverse("unlike", kwargs={"image_id": str(image.id)}))

        assert resp.status_code in (200, 302)
        assert not Like.objects.filter(user=user, image=image).exists()


@pytest.mark.django_db
class TestSaveViews:
    def test_save_requires_login(self, client):
        image = ImageFactory()
        resp = client.post(reverse("save", kwargs={"image_id": str(image.id)}))
        assert resp.status_code == 302
        assert "/login/" in resp["Location"]

    def test_save_creates_record(self, client):
        user = UserFactory()
        image = ImageFactory()
        client.force_login(user)

        client.post(reverse("save", kwargs={"image_id": str(image.id)}))

        assert Save.objects.filter(user=user, image=image).exists()

    def test_unsave_removes_record(self, client):
        user = UserFactory()
        image = ImageFactory(save_count=1)
        Save.objects.create(user=user, image=image)
        client.force_login(user)

        client.post(reverse("unsave", kwargs={"image_id": str(image.id)}))

        assert not Save.objects.filter(user=user, image=image).exists()


@pytest.mark.django_db
class TestDiscoverView:
    def test_returns_200(self, client):
        resp = client.get(reverse("discover"))
        assert resp.status_code == 200

    def test_htmx_returns_partial(self, client):
        ImageFactory.create_batch(3)
        resp = client.get(reverse("discover"), HTTP_HX_REQUEST="true")
        assert resp.status_code == 200
        assert b"<article" in resp.content
