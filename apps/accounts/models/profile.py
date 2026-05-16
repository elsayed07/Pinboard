from django.db import models

from shared.models import TimestampedModel


class PrivacyLevel(models.TextChoices):
    PUBLIC = "public", "Public"
    FOLLOWERS = "followers", "Followers only"
    PRIVATE = "private", "Private"


class Profile(TimestampedModel):
    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="profile",
    )
    full_name = models.CharField(max_length=120, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    privacy_level = models.CharField(
        max_length=20,
        choices=PrivacyLevel.choices,
        default=PrivacyLevel.PUBLIC,
    )

    class Meta:
        db_table = "accounts_profile"

    def __str__(self) -> str:
        return f"Profile({self.user.username})"

    @property
    def avatar_url(self) -> str:
        if self.avatar:
            return self.avatar.url
        return "/static/icons/default-avatar.svg"
