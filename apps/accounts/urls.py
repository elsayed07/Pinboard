from django.urls import path

from apps.accounts import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("settings/", views.settings_view, name="settings"),
    path("settings/avatar/", views.update_avatar_view, name="update-avatar"),
    path("<str:username>/", views.profile_view, name="profile"),
    path("<str:username>/follow/", views.follow_view, name="follow"),
    path("<str:username>/unfollow/", views.unfollow_view, name="unfollow"),
]
