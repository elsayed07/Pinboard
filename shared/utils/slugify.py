import uuid

from django.utils.text import slugify as django_slugify


def unique_slug(text: str, model_class, slug_field: str = "slug") -> str:
    base = django_slugify(text)[:80] or "item"
    slug = base
    while model_class._default_manager.filter(**{slug_field: slug}).exists():
        slug = f"{base}-{uuid.uuid4().hex[:6]}"
    return slug
