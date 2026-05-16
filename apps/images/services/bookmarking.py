import httpx
from django.core.files.base import ContentFile
from django.db import transaction

from apps.accounts.models import User
from apps.images.models import Image, ImageStatus
from apps.images.tasks import process_image_task
from shared.exceptions import ValidationError
from shared.utils.slugify import unique_slug
from shared.validators import validate_image_url


class BookmarkService:
    @staticmethod
    @transaction.atomic
    def bookmark_from_url(
        *,
        owner: User,
        url: str,
        title: str,
        description: str = "",
        tags: list[str] | None = None,
    ) -> Image:
        validate_image_url(url)

        try:
            response = httpx.get(url, timeout=10, follow_redirects=True)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ValidationError(f"Could not fetch image: {exc}")

        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("image/"):
            raise ValidationError("URL does not point to an image.")

        slug = unique_slug(title, Image)
        image = Image.objects.create(
            owner=owner,
            title=title,
            slug=slug,
            description=description,
            source_url=url,
            status=ImageStatus.PENDING,
        )

        ext = content_type.split("/")[-1].split(";")[0] or "jpg"
        image.image.save(f"{slug}.{ext}", ContentFile(response.content), save=True)

        if tags:
            image.tags.set(*tags)

        process_image_task.delay(str(image.id))
        return image

    @staticmethod
    @transaction.atomic
    def upload_image(
        *,
        owner: User,
        file,
        title: str,
        description: str = "",
        tags: list[str] | None = None,
    ) -> Image:
        from shared.validators import validate_image_file

        validate_image_file(file)

        slug = unique_slug(title, Image)
        image = Image.objects.create(
            owner=owner,
            title=title,
            slug=slug,
            description=description,
            status=ImageStatus.PENDING,
        )
        image.image.save(file.name, file, save=True)

        if tags:
            image.tags.set(*tags)

        process_image_task.delay(str(image.id))
        return image
