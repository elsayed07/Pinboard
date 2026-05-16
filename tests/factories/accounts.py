import factory
from factory.django import DjangoModelFactory

from apps.accounts.models import Follow, Profile, User


class UserFactory(DjangoModelFactory):
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    is_active = True

    class Meta:
        model = User

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return model_class.objects.create_user(*args, **kwargs)


class ProfileFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    bio = factory.Faker("sentence")
    full_name = factory.Faker("name")

    class Meta:
        model = Profile
        django_get_or_create = ["user"]


class FollowFactory(DjangoModelFactory):
    follower = factory.SubFactory(UserFactory)
    following = factory.SubFactory(UserFactory)

    class Meta:
        model = Follow
