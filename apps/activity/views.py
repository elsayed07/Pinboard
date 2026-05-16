from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.activity.services import ActivityService


@login_required
def feed_view(request: HttpRequest) -> HttpResponse:
    activities = ActivityService.get_feed(request.user)
    if request.htmx:
        return render(request, "components/activity_list.html", {"activities": activities})
    return render(request, "pages/activity/feed.html", {"activities": activities})
