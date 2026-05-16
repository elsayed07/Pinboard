import pytest

from apps.accounts.services.follow import FollowService
from shared.exceptions import ConflictError, ValidationError
from tests.factories.accounts import UserFactory


@pytest.mark.django_db
class TestFollowService:
    def test_follow_creates_relationship(self):
        follower = UserFactory()
        target = UserFactory()

        follow = FollowService.follow(follower=follower, target_id=str(target.id))

        assert follow.follower == follower
        assert follow.following == target

    def test_cannot_follow_self(self):
        user = UserFactory()
        with pytest.raises(ValidationError):
            FollowService.follow(follower=user, target_id=str(user.id))

    def test_cannot_follow_twice(self):
        follower = UserFactory()
        target = UserFactory()
        FollowService.follow(follower=follower, target_id=str(target.id))

        with pytest.raises(ConflictError):
            FollowService.follow(follower=follower, target_id=str(target.id))

    def test_unfollow_removes_relationship(self):
        follower = UserFactory()
        target = UserFactory()
        FollowService.follow(follower=follower, target_id=str(target.id))

        FollowService.unfollow(follower=follower, target_id=str(target.id))

        from apps.accounts.models import Follow
        assert not Follow.objects.filter(follower=follower, following=target).exists()
