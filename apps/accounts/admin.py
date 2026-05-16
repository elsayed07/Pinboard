from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.models import Block, Follow, Profile, User


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fields = ("full_name", "bio", "avatar", "website", "location", "privacy_level")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ("email", "username", "is_active", "is_staff", "date_joined")
    list_filter = ("is_active", "is_staff")
    search_fields = ("email", "username")
    ordering = ("-date_joined",)
    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("date_joined", "last_login")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "username", "password1", "password2")}),
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "following", "created_at")
    search_fields = ("follower__username", "following__username")
    raw_id_fields = ("follower", "following")


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ("blocker", "blocked", "created_at")
    raw_id_fields = ("blocker", "blocked")
