import pytest
from django.urls import reverse

from apps.accounts.models import Follow
from tests.factories.accounts import UserFactory


@pytest.mark.django_db
class TestRegisterView:
    def test_get_returns_form(self, client):
        resp = client.get(reverse("register"))
        assert resp.status_code == 200

    def test_valid_post_creates_user_and_redirects(self, client):
        resp = client.post(reverse("register"), {
            "email": "new@example.com",
            "username": "newuser",
            "password": "securepass123",
            "password2": "securepass123",
        })
        assert resp.status_code == 302
        from apps.accounts.models import User
        assert User.objects.filter(email="new@example.com").exists()

    def test_duplicate_email_shows_error(self, client):
        UserFactory(email="taken@example.com")
        resp = client.post(reverse("register"), {
            "email": "taken@example.com",
            "username": "someone",
            "password": "securepass123",
        })
        assert resp.status_code == 200

    def test_authenticated_user_redirects_home(self, client):
        user = UserFactory()
        client.force_login(user)
        resp = client.get(reverse("register"))
        assert resp.status_code == 302


@pytest.mark.django_db
class TestLoginView:
    def test_get_returns_form(self, client):
        resp = client.get(reverse("login"))
        assert resp.status_code == 200

    def test_valid_credentials_log_in(self, client):
        user = UserFactory()
        user.set_password("testpass123")
        user.save()

        resp = client.post(reverse("login"), {
            "email": user.email,
            "password": "testpass123",
        })
        assert resp.status_code == 302

    def test_invalid_credentials_stay_on_page(self, client):
        user = UserFactory()
        resp = client.post(reverse("login"), {
            "email": user.email,
            "password": "wrongpass",
        })
        assert resp.status_code == 200

    def test_authenticated_user_redirects_home(self, client):
        user = UserFactory()
        client.force_login(user)
        resp = client.get(reverse("login"))
        assert resp.status_code == 302


@pytest.mark.django_db
class TestLogoutView:
    def test_logout_redirects_to_login(self, client):
        user = UserFactory()
        client.force_login(user)
        resp = client.post(reverse("logout"))
        assert resp.status_code == 302
        assert "/login/" in resp["Location"]

    def test_logout_requires_post(self, client):
        user = UserFactory()
        client.force_login(user)
        resp = client.get(reverse("logout"))
        assert resp.status_code == 405


@pytest.mark.django_db
class TestProfileView:
    def test_existing_profile_returns_200(self, client):
        user = UserFactory()
        resp = client.get(reverse("profile", kwargs={"username": user.username}))
        assert resp.status_code == 200

    def test_unknown_username_returns_404(self, client):
        resp = client.get(reverse("profile", kwargs={"username": "nobody"}))
        assert resp.status_code == 404


@pytest.mark.django_db
class TestFollowViews:
    def test_follow_requires_login(self, client):
        target = UserFactory()
        resp = client.post(reverse("follow", kwargs={"username": target.username}))
        assert resp.status_code == 302
        assert "/login/" in resp["Location"]

    def test_follow_creates_relationship(self, client):
        follower = UserFactory()
        target = UserFactory()
        client.force_login(follower)

        resp = client.post(reverse("follow", kwargs={"username": target.username}))

        assert resp.status_code == 302
        assert Follow.objects.filter(follower=follower, following=target).exists()

    def test_unfollow_removes_relationship(self, client):
        follower = UserFactory()
        target = UserFactory()
        Follow.objects.create(follower=follower, following=target)
        client.force_login(follower)

        client.post(reverse("unfollow", kwargs={"username": target.username}))

        assert not Follow.objects.filter(follower=follower, following=target).exists()
