import structlog
from decouple import config

from .base import *  # noqa: F401, F403

DEBUG = False

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# ── Database connection pooling ───────────────────────────────────────────────
DATABASES["default"]["CONN_MAX_AGE"] = 60  # noqa: F405
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True  # noqa: F405

# ── Storage (Django 5.x STORAGES dict) ───────────────────────────────────────
_S3_BUCKET = config("AWS_STORAGE_BUCKET_NAME")
_S3_DOMAIN = config("AWS_S3_CUSTOM_DOMAIN", default="")

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "access_key": config("AWS_ACCESS_KEY_ID"),
            "secret_key": config("AWS_SECRET_ACCESS_KEY"),
            "bucket_name": _S3_BUCKET,
            "region_name": config("AWS_S3_REGION_NAME", default="us-east-1"),
            "file_overwrite": False,
            "default_acl": "private",
            "custom_domain": _S3_DOMAIN or None,
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = f"https://{_S3_DOMAIN}/" if _S3_DOMAIN else f"https://{_S3_BUCKET}.s3.amazonaws.com/"

# ── Email (SES or SMTP) ───────────────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="email-smtp.us-east-1.amazonaws.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

ADMINS = [("Admin", config("ADMIN_EMAIL", default="admin@pinboard.app"))]
SERVER_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@pinboard.app")

# ── Structured logging ────────────────────────────────────────────────────────
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        }
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.security": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}
