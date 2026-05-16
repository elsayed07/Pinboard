from django.db import models

from shared.models import TimestampedModel


class Follow(TimestampedModel):
    follower = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="following",
    )
    following = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="followers",
    )

    class Meta:
        db_table = "accounts_follow"
        unique_together = [("follower", "following")]
        indexes = [
            models.Index(fields=["follower", "created_at"]),
            models.Index(fields=["following", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.follower.username} → {self.following.username}"


class Block(TimestampedModel):
    blocker = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="blocking",
    )
    blocked = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="blocked_by",
    )

    class Meta:
        db_table = "accounts_block"
        unique_together = [("blocker", "blocked")]

    def __str__(self) -> str:
        return f"{self.blocker.username} blocked {self.blocked.username}"
