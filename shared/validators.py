from urllib.parse import urlparse

from django.core.exceptions import ValidationError


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_SIZE_MB = 10


def validate_image_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValidationError("Image URL must use http or https.")
    if not parsed.netloc:
        raise ValidationError("Invalid image URL.")


def validate_image_file(file) -> None:
    if hasattr(file, "content_type") and file.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValidationError(
            f"Unsupported image type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    size_mb = file.size / (1024 * 1024)
    if size_mb > MAX_IMAGE_SIZE_MB:
        raise ValidationError(f"Image must be under {MAX_IMAGE_SIZE_MB} MB.")
