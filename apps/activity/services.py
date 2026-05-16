from django.contrib.contenttypes.models import ContentType

from apps.accounts.models import User
from apps.activity.models import Activity, Verb


class ActivityService:
    @staticmethod
    def record(*, actor: User, verb: Verb, target) -> Activity:
        ct = ContentType.objects.get_for_model(target)
        return Activity.objects.create(
            actor=actor,
            verb=verb,
            target_content_type=ct,
            target_id=str(target.pk),
        )

    @staticmethod
    def get_feed(user: User, limit: int = 40):
        following_ids = user.following.values_list("following_id", flat=True)
        return (
            Activity.objects.filter(actor_id__in=following_ids)
            .select_related("actor", "actor__profile", "target_content_type")
            .order_by("-created_at")[:limit]
        )
