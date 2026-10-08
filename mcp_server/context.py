from contextvars import ContextVar

bearer_token: ContextVar[str | None] = ContextVar("bearer_token", default=None)
