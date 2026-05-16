from dataclasses import dataclass

from django.contrib.auth import authenticate
from django.db import transaction

from apps.accounts.models import Profile, User
from shared.exceptions import ConflictError, ValidationError


@dataclass
class TokenPair:
    access: str
    refresh: str


class AuthService:
    @staticmethod
    @transaction.atomic
    def register(*, email: str, username: str, password: str) -> User:
        if User.objects.filter(email=email).exists():
            raise ConflictError("An account with this email already exists.")
        if User.objects.filter(username=username).exists():
            raise ConflictError("This username is already taken.")

        user = User.objects.create_user(email=email, username=username, password=password)
        Profile.objects.create(user=user)
        return user

    @staticmethod
    def authenticate(*, email: str, password: str) -> User:
        user = authenticate(email=email, password=password)
        if user is None:
            raise ValidationError("Invalid email or password.")
        if not user.is_active:
            raise ValidationError("This account has been deactivated.")
        return user

    @staticmethod
    def get_tokens_for_user(user: User) -> TokenPair:
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        return TokenPair(access=str(refresh.access_token), refresh=str(refresh))
