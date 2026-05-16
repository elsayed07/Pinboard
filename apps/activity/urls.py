from django.urls import path
from apps.activity import views

urlpatterns = [
    path("", views.feed_view, name="activity-feed"),
]
