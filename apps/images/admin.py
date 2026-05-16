from django.contrib import admin

from apps.images.models import Collection, Image, Like, Save


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "status", "privacy", "like_count", "view_count", "created_at")
    list_filter = ("status", "privacy")
    search_fields = ("title", "owner__username", "slug")
    raw_id_fields = ("owner", "collection")
    readonly_fields = ("slug", "like_count", "view_count", "created_at", "updated_at")
    actions = ["mark_ready", "mark_moderated"]

    def mark_ready(self, request, queryset):
        queryset.update(status="ready")
    mark_ready.short_description = "Mark selected images as ready"

    def mark_moderated(self, request, queryset):
        queryset.update(status="moderated")
    mark_moderated.short_description = "Remove selected images (moderation)"


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "is_private", "created_at")
    search_fields = ("name", "owner__username")
    raw_id_fields = ("owner", "cover_image")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "image", "created_at")
    raw_id_fields = ("user", "image")


@admin.register(Save)
class SaveAdmin(admin.ModelAdmin):
    list_display = ("user", "image", "created_at")
    raw_id_fields = ("user", "image")
