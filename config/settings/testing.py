from .base import *  # noqa: F401, F403

DEBUG = False
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
AUTH_PASSWORD_VALIDATORS = []  # noqa: F405

DATABASES = {  # noqa: F405
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "pinboard_test",
        "USER": "pinboard",
        "PASSWORD": "pinboard",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

CACHES = {  # noqa: F405
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
}

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

MEDIA_ROOT = "/tmp/pinboard_test_media"
