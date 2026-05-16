from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from shared.models import TimestampedModel


class ReportReason(models.TextChoices):
    SPAM = "spam", "Spam"
    HARASSMENT = "harassment", "Harassment"
    NUDITY = "nudity", "Nudity or sexual content"
    VIOLENCE = "violence", "Violence"
    COPYRIGHT = "copyright", "Copyright infringement"
    OTHER = "other", "Other"


class ReportStatus(models.TextChoices):
    PENDING = "pending", "Pending review"
    RESOLVED = "resolved", "Resolved"
    DISMISSED = "dismissed", "Dismissed"


class Report(TimestampedModel):
    reporter = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="reports_filed",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=36)
    content_object = GenericForeignKey("content_type", "object_id")

    reason = models.CharField(max_length=30, choices=ReportReason.choices)
    detail = models.TextField(max_length=1000, blank=True)
    status = models.CharField(
        max_length=20,
        choices=ReportStatus.choices,
        default=ReportStatus.PENDING,
        db_index=True,
    )
    resolved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports_resolved",
    )

    class Meta:
        db_table = "moderation_report"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "-created_at"])]
