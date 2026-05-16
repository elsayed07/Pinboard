from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from shared.models import TimestampedModel


class Notification(TimestampedModel):
    recipient = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="notifications",
        db_index=True,
    )
    actor = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="sent_notifications",
    )
    verb = models.CharField(max_length=50)

    target_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    target_id = models.CharField(max_length=36, blank=True)
    target = GenericForeignKey("target_content_type", "target_id")

    read_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "notifications_notification"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "read_at", "-created_at"]),
        ]

    @property
    def is_read(self) -> bool:
        return self.read_at is not None
