from django.core.files.base import ContentFile

from apps.images.models import Image, ImageStatus
from shared.utils.images import compress_image, generate_thumbnail, get_image_dimensions, webp_filename


class ProcessingService:
    @staticmethod
    def process(image_id: str) -> None:
        try:
            image = Image.all_objects.get(id=image_id)
        except Image.DoesNotExist:
            return

        try:
            image.image.open("rb")

            width, height = get_image_dimensions(image.image)
            image.width = width
            image.height = height

            compressed = compress_image(image.image)
            new_name = webp_filename(image.image.name)
            image.image.save(new_name, ContentFile(compressed.read()), save=False)

            image.image.open("rb")
            thumb = generate_thumbnail(image.image)
            thumb_name = f"thumb_{new_name}"
            image.thumbnail.save(thumb_name, ContentFile(thumb.read()), save=False)

            image.status = ImageStatus.READY
            image.save(update_fields=["image", "thumbnail", "width", "height", "status", "updated_at"])

        except Exception:
            image.status = ImageStatus.FAILED
            image.save(update_fields=["status", "updated_at"])
            raise
