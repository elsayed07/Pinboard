from django.db import transaction

from apps.accounts.models import Block, Follow, User
from shared.cache import invalidate_user_feed
from shared.exceptions import ConflictError, NotFoundError, ValidationError


class FollowService:
    @staticmethod
    @transaction.atomic
    def follow(*, follower: User, target_id: str) -> Follow:
        try:
            target = User.objects.get(id=target_id)
        except User.DoesNotExist:
            raise NotFoundError("User not found.")

        if follower.id == target.id:
            raise ValidationError("You cannot follow yourself.")

        if Block.objects.filter(blocker=target, blocked=follower).exists():
            raise NotFoundError("User not found.")

        follow, created = Follow.objects.get_or_create(follower=follower, following=target)
        if not created:
            raise ConflictError("Already following this user.")

        invalidate_user_feed(str(follower.id))

        # Notify + record activity outside the atomic block to avoid holding locks
        transaction.on_commit(lambda: _post_follow(follower, target))
        return follow

    @staticmethod
    @transaction.atomic
    def unfollow(*, follower: User, target_id: str) -> None:
        deleted, _ = Follow.objects.filter(
            follower=follower, following_id=target_id
        ).delete()
        if not deleted:
            raise NotFoundError("Follow relationship not found.")
        invalidate_user_feed(str(follower.id))

    @staticmethod
    @transaction.atomic
    def block(*, blocker: User, target_id: str) -> Block:
        try:
            target = User.objects.get(id=target_id)
        except User.DoesNotExist:
            raise NotFoundError("User not found.")

        if blocker.id == target.id:
            raise ValidationError("You cannot block yourself.")

        Follow.objects.filter(follower=blocker, following=target).delete()
        Follow.objects.filter(follower=target, following=blocker).delete()

        block, _ = Block.objects.get_or_create(blocker=blocker, blocked=target)
        return block

    @staticmethod
    def unblock(*, blocker: User, target_id: str) -> None:
        Block.objects.filter(blocker=blocker, blocked_id=target_id).delete()


def _post_follow(follower: User, target: User) -> None:
    from apps.activity.models import Verb
    from apps.activity.services import ActivityService
    from apps.notifications.services import NotificationService

    ActivityService.record(actor=follower, verb=Verb.FOLLOWED, target=target)
    NotificationService.send(
        recipient=target,
        actor=follower,
        verb="started following you",
        target=target,
    )
