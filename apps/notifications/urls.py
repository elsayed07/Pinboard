from django.urls import path
from apps.notifications import views

urlpatterns = [
    path("", views.list_view, name="notifications"),
    path("<str:notification_id>/read/", views.mark_read_view, name="notification-read"),
    path("read-all/", views.mark_all_read_view, name="notifications-read-all"),
]
