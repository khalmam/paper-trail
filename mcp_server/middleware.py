from .context import bearer_token


class BearerTokenMiddleware:
    """Pure ASGI middleware: copies `Authorization: Bearer <token>` into a context variable
    so tools can read it without depending on SDK internals."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        token = None
        for key, value in scope["headers"]:
            if key == b"authorization":
                text = value.decode()
                if text.lower().startswith("bearer "):
                    token = text[7:].strip()
        reset = bearer_token.set(token)
        try:
            await self.app(scope, receive, send)
        finally:
            bearer_token.reset(reset)
