from django.urls import path

from apps.images import views

urlpatterns = [
    path("bookmark/", views.bookmark_view, name="bookmark"),
    path("upload/", views.upload_view, name="upload"),
    path("discover/", views.discover_view, name="discover"),
    path("<str:slug>/", views.image_detail_view, name="image-detail"),
    path("<str:image_id>/like/", views.like_view, name="like"),
    path("<str:image_id>/unlike/", views.unlike_view, name="unlike"),
    path("<str:image_id>/save/", views.save_view, name="save"),
    path("<str:image_id>/unsave/", views.unsave_view, name="unsave"),
]
