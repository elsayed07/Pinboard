from .base import *  # noqa: F401, F403
from decouple import config

DEBUG = True
INTERNAL_IPS = config("INTERNAL_IPS", default="127.0.0.1", cast=lambda v: v.split(","))

INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    *MIDDLEWARE,  # noqa: F405
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Relax password validators locally
AUTH_PASSWORD_VALIDATORS = []  # noqa: F405

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "DEBUG"},
}
