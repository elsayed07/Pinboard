from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from shared.models import TimestampedModel


class Verb(models.TextChoices):
    LIKED = "liked", "liked"
    SAVED = "saved", "saved"
    FOLLOWED = "followed", "followed"
    BOOKMARKED = "bookmarked", "bookmarked"
    COMMENTED = "commented", "commented"


class Activity(TimestampedModel):
    actor = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="activities",
        db_index=True,
    )
    verb = models.CharField(max_length=30, choices=Verb.choices, db_index=True)

    target_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    target_id = models.CharField(max_length=36, blank=True, db_index=True)
    target = GenericForeignKey("target_content_type", "target_id")

    class Meta:
        db_table = "activity_activity"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["actor", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.actor.username} {self.verb}"
