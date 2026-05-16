from django.urls import path

from apps.moderation import views

urlpatterns = [
    path("report/image/<str:image_id>/", views.report_image_view, name="report-image"),
]
