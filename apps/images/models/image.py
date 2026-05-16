from django.contrib.postgres.search import SearchVectorField
from django.db import models
from taggit.managers import TaggableManager
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase

from shared.models import BaseModel


class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    """Through model that stores UUID object_ids for taggit."""

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"


class ImageStatus(models.TextChoices):
    PENDING = "pending", "Pending processing"
    READY = "ready", "Ready"
    FAILED = "failed", "Failed"
    MODERATED = "moderated", "Removed by moderation"


class ImagePrivacy(models.TextChoices):
    PUBLIC = "public", "Public"
    FOLLOWERS = "followers", "Followers only"
    PRIVATE = "private", "Private"


class Image(BaseModel):
    owner = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="images",
        db_index=True,
    )
    collection = models.ForeignKey(
        "images.Collection",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="images",
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, db_index=True)
    description = models.TextField(max_length=1000, blank=True)
    source_url = models.URLField(max_length=2000, blank=True)

    # Stored files
    image = models.ImageField(upload_to="images/originals/", blank=True)
    thumbnail = models.ImageField(upload_to="images/thumbnails/", blank=True)

    # Dimensions
    width = models.PositiveIntegerField(default=0)
    height = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=20, choices=ImageStatus.choices, default=ImageStatus.PENDING, db_index=True
    )
    privacy = models.CharField(
        max_length=20, choices=ImagePrivacy.choices, default=ImagePrivacy.PUBLIC, db_index=True
    )

    # Denormalised counters (Redis is source of truth, synced periodically)
    view_count = models.PositiveBigIntegerField(default=0, db_index=True)
    like_count = models.PositiveBigIntegerField(default=0, db_index=True)
    save_count = models.PositiveIntegerField(default=0)

    tags = TaggableManager(through=UUIDTaggedItem, blank=True)
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        db_table = "images_image"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["status", "privacy", "-created_at"]),
            models.Index(fields=["-like_count"]),
            models.Index(fields=["-view_count"]),
        ]

    def __str__(self) -> str:
        return self.title
