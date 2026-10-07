"""Bridge from async MCP tools to the sync service layer."""
from asgiref.sync import sync_to_async
from django.db import close_old_connections


async def run_db(fn, /, *args, **kwargs):
    def call():
        try:
            return fn(*args, **kwargs)
        finally:
            close_old_connections()  # MCP calls don't trigger Django's request signals
    return await sync_to_async(call, thread_sensitive=True)()
