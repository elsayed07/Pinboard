from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from django.urls import include, path

from api.v1 import api


def health_check(request):
    return JsonResponse({"status": "ok"})


_reset_kwargs = {
    "template_name": "pages/auth/password_reset.html",
    "email_template_name": "pages/auth/password_reset_email.txt",
    "subject_template_name": "pages/auth/password_reset_subject.txt",
}

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    # Password reset (Django built-in, styled to match the app)
    path(
        "accounts/password-reset/",
        auth_views.PasswordResetView.as_view(
            **_reset_kwargs,
            success_url="/accounts/password-reset/done/",
        ),
        name="password-reset",
    ),
    path(
        "accounts/password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="pages/auth/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "accounts/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="pages/auth/password_reset_confirm.html",
            success_url="/accounts/reset/done/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "accounts/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="pages/auth/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    path("images/", include("apps.images.urls")),
    path("activity/", include("apps.activity.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("search/", include("apps.search.urls")),
    path("moderation/", include("apps.moderation.urls")),
    path("social/", include("social_django.urls", namespace="social")),
    path("api/v1/", api.urls),
    path("", include("apps.images.urls_home")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
