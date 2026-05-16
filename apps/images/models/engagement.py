from django.db import models

from shared.models import TimestampedModel


class Like(TimestampedModel):
    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="likes"
    )
    image = models.ForeignKey(
        "images.Image", on_delete=models.CASCADE, related_name="likes"
    )

    class Meta:
        db_table = "images_like"
        unique_together = [("user", "image")]
        indexes = [models.Index(fields=["image", "-created_at"])]


class Save(TimestampedModel):
    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="saves"
    )
    image = models.ForeignKey(
        "images.Image", on_delete=models.CASCADE, related_name="saves"
    )

    class Meta:
        db_table = "images_save"
        unique_together = [("user", "image")]
