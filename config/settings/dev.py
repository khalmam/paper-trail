import os

os.environ.setdefault("DATABASE_URL", "postgres://papertrail:papertrail@localhost:5432/papertrail")

from .base import *  # noqa: E402,F401,F403

DEBUG = True
SECRET_KEY = "dev-only-insecure-key"
ALLOWED_HOSTS = ["*"]

MCP_DEV_IDENTITY = True
