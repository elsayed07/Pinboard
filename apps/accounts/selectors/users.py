from django.db.models import Count, QuerySet

from apps.accounts.models import Follow, User


class UserSelector:
    @staticmethod
    def get_by_id(user_id: str) -> User:
        return (
            User.objects.select_related("profile")
            .get(id=user_id)
        )

    @staticmethod
    def get_by_username(username: str) -> User:
        return (
            User.objects.select_related("profile")
            .get(username=username)
        )

    @staticmethod
    def get_followers(user: User) -> QuerySet[User]:
        return (
            User.objects.filter(following__following=user)
            .select_related("profile")
            .order_by("-following__created_at")
        )

    @staticmethod
    def get_following(user: User) -> QuerySet[User]:
        return (
            User.objects.filter(followers__follower=user)
            .select_related("profile")
            .order_by("-followers__created_at")
        )

    @staticmethod
    def is_following(follower: User, target: User) -> bool:
        return Follow.objects.filter(follower=follower, following=target).exists()

    @staticmethod
    def search(query: str, exclude_user: User | None = None) -> QuerySet[User]:
        qs = (
            User.objects.select_related("profile")
            .filter(username__icontains=query)
            .annotate(follower_count=Count("followers"))
            .order_by("-follower_count")
        )
        if exclude_user:
            qs = qs.exclude(id=exclude_user.id)
        return qs[:20]
