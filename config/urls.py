from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from api.v1 import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("images/", include("apps.images.urls")),
    path("activity/", include("apps.activity.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("search/", include("apps.search.urls")),
    path("social/", include("social_django.urls", namespace="social")),
    path("api/v1/", api.urls),
    path("", include("apps.images.urls_home")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
