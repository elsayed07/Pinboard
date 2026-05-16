from django.urls import path

from apps.images import views

urlpatterns = [
    path("bookmark/", views.bookmark_view, name="bookmark"),
    path("upload/", views.upload_view, name="upload"),
    path("discover/", views.discover_view, name="discover"),
    path("collections/", views.collections_view, name="collections"),
    path("collections/<str:collection_id>/", views.collection_detail_view, name="collection-detail"),
    path("collections/<str:collection_id>/add/<str:image_id>/", views.collection_add_image_view, name="collection-add-image"),
    path("<str:image_id>/remove-from-collection/", views.collection_remove_image_view, name="collection-remove-image"),
    path("<str:image_id>/like/", views.like_view, name="like"),
    path("<str:image_id>/unlike/", views.unlike_view, name="unlike"),
    path("<str:image_id>/save/", views.save_view, name="save"),
    path("<str:image_id>/unsave/", views.unsave_view, name="unsave"),
    path("<str:slug>/", views.image_detail_view, name="image-detail"),
]
