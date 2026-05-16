from django.contrib.contenttypes.models import ContentType

from apps.accounts.models import User
from apps.moderation.models import Report, ReportReason


class ModerationService:
    @staticmethod
    def report(
        *,
        reporter: User,
        target,
        reason: ReportReason,
        detail: str = "",
    ) -> Report:
        ct = ContentType.objects.get_for_model(target)
        report, _ = Report.objects.get_or_create(
            reporter=reporter,
            content_type=ct,
            object_id=str(target.pk),
            defaults={"reason": reason, "detail": detail},
        )
        return report
