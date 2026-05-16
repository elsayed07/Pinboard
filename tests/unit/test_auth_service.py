import pytest

from apps.accounts.services.auth import AuthService
from shared.exceptions import ConflictError, ValidationError
from tests.factories.accounts import UserFactory


@pytest.mark.django_db
class TestAuthService:
    def test_register_creates_user_and_profile(self):
        user = AuthService.register(
            email="newuser@example.com",
            username="newuser",
            password="securepass123",
        )
        assert user.email == "newuser@example.com"
        assert hasattr(user, "profile")

    def test_register_duplicate_email_raises(self):
        UserFactory(email="taken@example.com")
        with pytest.raises(ConflictError):
            AuthService.register(
                email="taken@example.com",
                username="other",
                password="pass123",
            )

    def test_register_duplicate_username_raises(self):
        UserFactory(username="taken")
        with pytest.raises(ConflictError):
            AuthService.register(
                email="new@example.com",
                username="taken",
                password="pass123",
            )

    def test_authenticate_invalid_credentials_raises(self):
        UserFactory(email="test@example.com")
        with pytest.raises(ValidationError):
            AuthService.authenticate(email="test@example.com", password="wrongpass")
