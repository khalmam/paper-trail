"""Settings shared by every environment. No environment-specific defaults here."""
from pathlib import Path

import dj_database_url

from config import env

BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "ledger",
]
MIDDLEWARE: list[str] = []
ROOT_URLCONF = "config.urls"

# conn_max_age=0: MCP tools run via sync_to_async in worker threads, so we never
# want long-lived per-thread connections (see mcp_server/runner.py).
DATABASES = {
    "default": dj_database_url.parse(env.require("DATABASE_URL"), conn_max_age=0),
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
TIME_ZONE = "UTC"

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": env.get("LOG_LEVEL", "INFO")},
}
