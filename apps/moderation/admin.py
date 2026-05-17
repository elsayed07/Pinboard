from django.contrib import admin
from django.utils import timezone

from apps.moderation.models import Report, ReportStatus


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["id", "reporter", "reason", "status", "content_type", "object_id", "created_at"]
    list_filter = ["status", "reason", "content_type"]
    search_fields = ["reporter__email", "reporter__username", "detail"]
    readonly_fields = ["reporter", "content_type", "object_id", "reason", "detail", "created_at"]
    actions = ["resolve_reports", "dismiss_reports"]

    @admin.action(description="Mark selected reports as resolved")
    def resolve_reports(self, request, queryset):
        updated = queryset.filter(status=ReportStatus.PENDING).update(
            status=ReportStatus.RESOLVED,
            resolved_by=request.user,
        )
        self.message_user(request, f"{updated} report(s) resolved.")

    @admin.action(description="Dismiss selected reports")
    def dismiss_reports(self, request, queryset):
        updated = queryset.filter(status=ReportStatus.PENDING).update(
            status=ReportStatus.DISMISSED,
            resolved_by=request.user,
        )
        self.message_user(request, f"{updated} report(s) dismissed.")
