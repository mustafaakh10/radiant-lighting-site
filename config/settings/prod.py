from .base import *  # noqa: F401,F403

DEBUG = False
if SECRET_KEY == "dev-only-not-secret":  # noqa: F405
    raise RuntimeError("Set DJANGO_SECRET_KEY in production.")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env_bool("DJANGO_SSL_REDIRECT", True)  # noqa: F405
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "SAMEORIGIN"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
