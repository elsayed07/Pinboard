from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from apps.accounts.models import User
from apps.notifications.models import Notification


class NotificationService:
    @staticmethod
    def send(*, recipient: User, actor: User, verb: str, target=None) -> Notification:
        if recipient.id == actor.id:
            return None  # type: ignore[return-value]

        ct = target_id = None
        if target is not None:
            from django.contrib.contenttypes.models import ContentType
            ct = ContentType.objects.get_for_model(target)
            target_id = str(target.pk)

        notification = Notification.objects.create(
            recipient=recipient,
            actor=actor,
            verb=verb,
            target_content_type=ct,
            target_id=target_id or "",
        )

        NotificationService._push_ws(notification)
        return notification

    @staticmethod
    def _push_ws(notification: Notification) -> None:
        channel_layer = get_channel_layer()
        group_name = f"notifications_{notification.recipient_id}"
        try:
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "notify",
                    "id": str(notification.id),
                    "verb": notification.verb,
                    "actor": notification.actor.username,
                    "created_at": notification.created_at.isoformat(),
                },
            )
        except Exception:
            pass

    @staticmethod
    def mark_read(*, user: User, notification_id: str) -> None:
        Notification.objects.filter(
            recipient=user, id=notification_id, read_at__isnull=True
        ).update(read_at=timezone.now())

    @staticmethod
    def mark_all_read(user: User) -> int:
        return Notification.objects.filter(
            recipient=user, read_at__isnull=True
        ).update(read_at=timezone.now())
