import factory
from factory.django import DjangoModelFactory

from apps.images.models import Collection, Image, ImageStatus
from tests.factories.accounts import UserFactory


class ImageFactory(DjangoModelFactory):
    owner = factory.SubFactory(UserFactory)
    title = factory.Faker("sentence", nb_words=4)
    slug = factory.Sequence(lambda n: f"image-slug-{n}")
    description = factory.Faker("paragraph")
    status = ImageStatus.READY
    privacy = "public"

    class Meta:
        model = Image


class CollectionFactory(DjangoModelFactory):
    owner = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Collection {n}")

    class Meta:
        model = Collection
