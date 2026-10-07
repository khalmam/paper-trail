"""Production: everything explicit, nothing insecure by default."""
from config import env

from .base import *  # noqa: F401,F403
from .base import DATABASES

DEBUG = False
SECRET_KEY = env.require("SECRET_KEY")
ALLOWED_HOSTS = env.csv("ALLOWED_HOSTS") or env.require("ALLOWED_HOSTS").split(",")

DATABASES["default"].setdefault("OPTIONS", {})["sslmode"] = env.get("DB_SSLMODE", "prefer")

if env.get("STORAGE_BACKEND") == "s3":
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "bucket_name": env.require("AWS_STORAGE_BUCKET_NAME"),
                "endpoint_url": env.get("AWS_S3_ENDPOINT_URL"),
            },
        },
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
