from django.core.cache import cache
from django.http import HttpRequest

from shared.cache import CacheKey

_TTL = 30


def unread_notifications(request: HttpRequest) -> dict:
    if not request.user.is_authenticated:
        return {"unread_notifications_count": 0}

    key = CacheKey.unread_notifications(str(request.user.id))
    count = cache.get(key)
    if count is None:
        count = request.user.notifications.filter(read_at__isnull=True).count()
        cache.set(key, count, timeout=_TTL)
    return {"unread_notifications_count": count}
