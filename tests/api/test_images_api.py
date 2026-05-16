import pytest
from django.test import Client
from django.urls import reverse

from apps.accounts.services.auth import AuthService
from apps.images.models import Like
from tests.factories.accounts import UserFactory
from tests.factories.images import ImageFactory


def _auth_header(user) -> dict:
    tokens = AuthService.get_tokens_for_user(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {tokens.access}"}


@pytest.mark.django_db
class TestTrendingEndpoint:
    def test_returns_200_unauthenticated(self, client):
        ImageFactory.create_batch(3)
        resp = client.get("/api/v1/images/trending/")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 3

    def test_image_shape(self, client):
        ImageFactory()
        resp = client.get("/api/v1/images/trending/")
        item = resp.json()[0]
        assert "id" in item
        assert "title" in item
        assert "slug" in item
        assert "like_count" in item
        assert "owner_username" in item


@pytest.mark.django_db
class TestFeedEndpoint:
    def test_requires_auth(self, client):
        resp = client.get("/api/v1/images/feed/")
        assert resp.status_code == 401

    def test_returns_following_images(self, client):
        user = UserFactory()
        followed = UserFactory()
        user.following.create(following=followed)
        ImageFactory.create_batch(2, owner=followed)
        ImageFactory()  # unrelated image

        resp = client.get("/api/v1/images/feed/", **_auth_header(user))

        assert resp.status_code == 200
        data = resp.json()["items"]
        assert len(data) == 2
        assert all(item["owner_username"] == followed.username for item in data)


@pytest.mark.django_db
class TestLikeEndpoint:
    def test_like_creates_record(self, client):
        user = UserFactory()
        image = ImageFactory()

        resp = client.post(f"/api/v1/images/{image.id}/like/", **_auth_header(user))

        assert resp.status_code == 201
        assert Like.objects.filter(user=user, image=image).exists()

    def test_like_requires_auth(self, client):
        image = ImageFactory()
        resp = client.post(f"/api/v1/images/{image.id}/like/")
        assert resp.status_code == 401

    def test_like_twice_returns_409(self, client):
        user = UserFactory()
        image = ImageFactory()
        Like.objects.create(user=user, image=image)

        resp = client.post(f"/api/v1/images/{image.id}/like/", **_auth_header(user))

        assert resp.status_code == 409

    def test_unlike_removes_record(self, client):
        user = UserFactory()
        image = ImageFactory(like_count=1)
        Like.objects.create(user=user, image=image)

        resp = client.delete(f"/api/v1/images/{image.id}/like/", **_auth_header(user))

        assert resp.status_code == 204
        assert not Like.objects.filter(user=user, image=image).exists()

    def test_unlike_nonexistent_returns_404(self, client):
        user = UserFactory()
        image = ImageFactory()

        resp = client.delete(f"/api/v1/images/{image.id}/like/", **_auth_header(user))

        assert resp.status_code == 404


@pytest.mark.django_db
class TestViewEndpoint:
    def test_record_view_returns_count(self, client):
        image = ImageFactory()

        resp = client.post(f"/api/v1/images/{image.id}/view/")

        assert resp.status_code == 200
        assert resp.json()["views"] == 1

    def test_record_view_increments(self, client):
        image = ImageFactory()
        client.post(f"/api/v1/images/{image.id}/view/")
        resp = client.post(f"/api/v1/images/{image.id}/view/")
        assert resp.json()["views"] == 2
