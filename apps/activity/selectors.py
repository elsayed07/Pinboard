from django.db.models import QuerySet

from apps.accounts.models import User
from apps.activity.models import Activity


class ActivitySelector:
    @staticmethod
    def get_feed(user: User, limit: int = 40) -> QuerySet[Activity]:
        following_ids = user.following.values_list("following_id", flat=True)
        return (
            Activity.objects.filter(actor_id__in=following_ids)
            .select_related("actor", "actor__profile", "target_content_type")
            .order_by("-created_at")[:limit]
        )