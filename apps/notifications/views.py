from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from apps.notifications.models import Notification
from apps.notifications.services import NotificationService


@login_required
def list_view(request: HttpRequest) -> HttpResponse:
    notifications = (
        Notification.objects.filter(recipient=request.user)
        .select_related("actor", "actor__profile")
        .order_by("-created_at")[:40]
    )
    return render(request, "pages/notifications/list.html", {"notifications": notifications})


@login_required
@require_POST
def mark_read_view(request: HttpRequest, notification_id: str) -> HttpResponse:
    NotificationService.mark_read(user=request.user, notification_id=notification_id)
    return HttpResponse(status=204)


@login_required
@require_POST
def mark_all_read_view(request: HttpRequest) -> HttpResponse:
    NotificationService.mark_all_read(request.user)
    return HttpResponse(status=204, headers={"HX-Trigger": "notificationsRead"})
