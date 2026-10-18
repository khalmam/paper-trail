"""POST /api/chat. Thin adapter: rules in chat_core decide, the MCP server acts."""
import asyncio
from datetime import date

import httpx
from django.conf import settings
from ninja import NinjaAPI, Schema

from ai.fake import FakeParser
from ai.guards import CallBudget

from .chat_core import route
from .mcp_client import ToolError, call_tool

api = NinjaAPI(urls_namespace="chat-api", docs_url=None)  # no public docs page

_budget = CallBudget(getattr(settings, "AI_DAILY_CALL_LIMIT", 100))
_parser = FakeParser()  # swapped for the Bedrock parser later; same interface
_client = httpx.Client(timeout=20)


class ChatIn(Schema):
    message: str
    token: str
    pending: dict | None = None


@api.post("/chat")
async def chat(request, body: ChatIn):
    action = await asyncio.to_thread(route, body.message, date.today(), _parser, _budget, body.pending)
    if action.tool is None:
        return {"speech": action.reply, "tool": None, "data": None, "pending": action.pending}
    url = getattr(settings, "MCP_URL", "http://127.0.0.1:8000/mcp")
    try:
        data = await asyncio.to_thread(call_tool, _client, url, body.token, action.tool, action.arguments)
    except ToolError as exc:
        return api.create_response(
            request, {"speech": str(exc), "tool": action.tool, "data": None, "pending": None}, status=502)
    return {"speech": data.get("speech") or "Done.", "tool": action.tool, "data": data, "pending": None}
