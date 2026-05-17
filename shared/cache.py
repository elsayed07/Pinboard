from django.core.cache import cache


class CacheKey:
    @staticmethod
    def image_views(image_id: str) -> str:
        return f"image:views:{image_id}"

    @staticmethod
    def image_likes(image_id: str) -> str:
        return f"image:likes:{image_id}"

    @staticmethod
    def user_feed(user_id: str, page: int = 1) -> str:
        return f"user:feed:{user_id}:{page}"

    @staticmethod
    def trending_images(period: str = "day") -> str:
        return f"trending:images:{period}"

    @staticmethod
    def user_following(user_id: str) -> str:
        return f"user:following:{user_id}"

    @staticmethod
    def user_profile(user_id: str) -> str:
        return f"user:profile:{user_id}"

    @staticmethod
    def unread_notifications(user_id: str) -> str:
        return f"user:unread_notifications:{user_id}"


def invalidate_user_feed(user_id: str, pages: int = 5) -> None:
    keys = [CacheKey.user_feed(user_id, p) for p in range(1, pages + 1)]
    cache.delete_many(keys)
