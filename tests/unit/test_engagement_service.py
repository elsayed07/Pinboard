import pytest

from apps.images.models import Image, Like, Save
from apps.images.services.engagement import EngagementService
from shared.exceptions import ConflictError, NotFoundError
from tests.factories.accounts import UserFactory
from tests.factories.images import ImageFactory


@pytest.mark.django_db
class TestEngagementLike:
    def test_like_creates_record_and_increments_count(self):
        user = UserFactory()
        image = ImageFactory(like_count=0)

        EngagementService.like(user=user, image_id=str(image.id))

        assert Like.objects.filter(user=user, image=image).exists()
        image.refresh_from_db()
        assert image.like_count == 1

    def test_like_nonexistent_image_raises(self):
        user = UserFactory()
        with pytest.raises(NotFoundError):
            EngagementService.like(user=user, image_id="00000000-0000-0000-0000-000000000000")

    def test_like_twice_raises_conflict(self):
        user = UserFactory()
        image = ImageFactory()
        EngagementService.like(user=user, image_id=str(image.id))

        with pytest.raises(ConflictError):
            EngagementService.like(user=user, image_id=str(image.id))

    def test_unlike_removes_record_and_decrements_count(self):
        user = UserFactory()
        image = ImageFactory(like_count=1)
        Like.objects.create(user=user, image=image)

        EngagementService.unlike(user=user, image_id=str(image.id))

        assert not Like.objects.filter(user=user, image=image).exists()
        image.refresh_from_db()
        assert image.like_count == 0

    def test_unlike_nonexistent_like_raises(self):
        user = UserFactory()
        image = ImageFactory()

        with pytest.raises(NotFoundError):
            EngagementService.unlike(user=user, image_id=str(image.id))


@pytest.mark.django_db
class TestEngagementSave:
    def test_save_creates_record_and_increments_count(self):
        user = UserFactory()
        image = ImageFactory(save_count=0)

        EngagementService.save_image(user=user, image_id=str(image.id))

        assert Save.objects.filter(user=user, image=image).exists()
        image.refresh_from_db()
        assert image.save_count == 1

    def test_save_twice_raises_conflict(self):
        user = UserFactory()
        image = ImageFactory()
        EngagementService.save_image(user=user, image_id=str(image.id))

        with pytest.raises(ConflictError):
            EngagementService.save_image(user=user, image_id=str(image.id))

    def test_unsave_removes_record_and_decrements_count(self):
        user = UserFactory()
        image = ImageFactory(save_count=1)
        Save.objects.create(user=user, image=image)

        EngagementService.unsave_image(user=user, image_id=str(image.id))

        assert not Save.objects.filter(user=user, image=image).exists()
        image.refresh_from_db()
        assert image.save_count == 0

    def test_unsave_nonexistent_raises(self):
        user = UserFactory()
        image = ImageFactory()

        with pytest.raises(NotFoundError):
            EngagementService.unsave_image(user=user, image_id=str(image.id))


@pytest.mark.django_db
class TestEngagementView:
    def test_record_view_increments(self):
        image = ImageFactory()
        count = EngagementService.record_view(image_id=str(image.id))
        assert count == 1
        count2 = EngagementService.record_view(image_id=str(image.id))
        assert count2 == 2
