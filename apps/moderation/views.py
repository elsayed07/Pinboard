from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from apps.images.models import Image
from apps.moderation.models import ReportReason
from apps.moderation.services import ModerationService
from shared.exceptions import ApplicationError


@login_required
@require_POST
def report_image_view(request: HttpRequest, image_id: str) -> HttpResponse:
    image = get_object_or_404(Image, id=image_id, status="ready")
    reason_value = request.POST.get("reason", ReportReason.OTHER)
    try:
        reason = ReportReason(reason_value)
    except ValueError:
        reason = ReportReason.OTHER

    ModerationService.report(
        reporter=request.user,
        target=image,
        reason=reason,
        detail=request.POST.get("detail", "")[:1000],
    )

    if request.htmx:
        return HttpResponse(
            '<p class="text-sm text-emerald-400 text-center py-2">Report submitted. Thank you.</p>'
        )
    return redirect("image-detail", slug=image.slug)
