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

