from django.http import HttpRequest


def unread_notifications(request: HttpRequest) -> dict:
    if not request.user.is_authenticated:
        return {"unread_notifications_count": 0}
    count = request.user.notifications.filter(read_at__isnull=True).count()
    return {"unread_notifications_count": count}
