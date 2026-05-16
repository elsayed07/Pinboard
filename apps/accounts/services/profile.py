from django.core.files import File

from apps.accounts.models import Profile, User
from shared.exceptions import NotFoundError


class ProfileService:
    @staticmethod
    def get_profile(user: User) -> Profile:
        try:
            return user.profile
        except Profile.DoesNotExist:
            raise NotFoundError("Profile not found.")

    @staticmethod
    def update_profile(
        user: User,
        *,
        full_name: str | None = None,
        bio: str | None = None,
        website: str | None = None,
        location: str | None = None,
        privacy_level: str | None = None,
    ) -> Profile:
        profile = ProfileService.get_profile(user)
        fields = []

        if full_name is not None:
            profile.full_name = full_name
            fields.append("full_name")
        if bio is not None:
            profile.bio = bio
            fields.append("bio")
        if website is not None:
            profile.website = website
            fields.append("website")
        if location is not None:
            profile.location = location
            fields.append("location")
        if privacy_level is not None:
            profile.privacy_level = privacy_level
            fields.append("privacy_level")

        if fields:
            fields.append("updated_at")
            profile.save(update_fields=fields)

        return profile

    @staticmethod
    def update_avatar(user: User, avatar: File) -> Profile:
        profile = ProfileService.get_profile(user)
        profile.avatar = avatar
        profile.save(update_fields=["avatar", "updated_at"])
        return profile
