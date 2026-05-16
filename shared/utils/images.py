import io
from pathlib import Path

from PIL import Image


MAX_DIMENSION = 2048
THUMBNAIL_SIZE = (400, 400)
WEBP_QUALITY = 85


def compress_image(image_file, max_dimension: int = MAX_DIMENSION) -> io.BytesIO:
    img = Image.open(image_file)
    img = img.convert("RGB")

    if img.width > max_dimension or img.height > max_dimension:
        img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)

    output = io.BytesIO()
    img.save(output, format="WEBP", quality=WEBP_QUALITY, optimize=True)
    output.seek(0)
    return output


def generate_thumbnail(image_file) -> io.BytesIO:
    img = Image.open(image_file)
    img = img.convert("RGB")
    img.thumbnail(THUMBNAIL_SIZE, Image.LANCZOS)

    output = io.BytesIO()
    img.save(output, format="WEBP", quality=80)
    output.seek(0)
    return output


def get_image_dimensions(image_file) -> tuple[int, int]:
    img = Image.open(image_file)
    return img.width, img.height


def webp_filename(original: str) -> str:
    return Path(original).stem + ".webp"
