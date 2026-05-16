from celery import shared_task


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def process_image_task(self, image_id: str) -> None:
    from apps.images.services.processing import ProcessingService

    try:
        ProcessingService.process(image_id)
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task
def sync_view_counts() -> None:
    """Periodic task: flush Redis view counts into the database."""
    from django.core.cache import cache
    from apps.images.models import Image

    images = Image.objects.filter(status="ready").only("id", "view_count")
    for image in images:
        key = f"image:views:{image.id}"
        redis_count = cache.get(key)
        if redis_count is not None and int(redis_count) != image.view_count:
            Image.objects.filter(id=image.id).update(view_count=int(redis_count))


@shared_task
def sync_like_counts() -> None:
    from django.core.cache import cache
    from apps.images.models import Like, Image
    from django.db.models import Count

    counts = Like.objects.values("image_id").annotate(total=Count("id"))
    for row in counts:
        Image.objects.filter(id=row["image_id"]).update(like_count=row["total"])
