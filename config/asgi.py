"""Composition root. Starlette owns the lifespan; /mcp -> MCP SDK app; everything else -> Django."""
import contextlib
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")  # safe default

from django.core.asgi import get_asgi_application

django_app = get_asgi_application()  # runs django.setup(); must precede importing models

from starlette.applications import Starlette
from starlette.routing import Mount, Route

from mcp_server.app import build_mcp
from mcp_server.middleware import BearerTokenMiddleware

mcp = build_mcp()
sdk_app = mcp.streamable_http_app()  # serves at /mcp by default


@contextlib.asynccontextmanager
async def lifespan(_app):
    async with mcp.session_manager.run():  # mounted sub-apps' lifespans are NOT run for you
        yield


application = Starlette(
    routes=[
        Route("/mcp", BearerTokenMiddleware(sdk_app)),        # exact path: no 307 to /mcp/, scope passes through untouched
        Mount("/", app=django_app),    # Django (+ Ninja later)
    ],
    lifespan=lifespan,
)
