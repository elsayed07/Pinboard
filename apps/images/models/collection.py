from django.db import models

from shared.models import BaseModel


class Collection(BaseModel):
    owner = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="collections",
    )
    name = models.CharField(max_length=150)
    description = models.TextField(max_length=500, blank=True)
    cover_image = models.ForeignKey(
        "images.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    is_private = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = "images_collection"
        unique_together = [("owner", "name")]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.owner.username}/{self.name}"
