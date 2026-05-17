import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("pinboard")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Flush Redis view counts into the DB every 10 minutes
    "sync-view-counts": {
        "task": "apps.images.tasks.sync_view_counts",
        "schedule": crontab(minute="*/10"),
    },
    # Reconcile like counts from DB once per hour (truth check vs denormalised counter)
    "sync-like-counts": {
        "task": "apps.images.tasks.sync_like_counts",
        "schedule": crontab(minute=0),
    },
}
