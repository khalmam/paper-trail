"""POST /api/chat. Thin adapter: rules in chat_core decide, the MCP server acts."""
import asyncio
from datetime import date

import httpx
from django.conf import settings
from django.http import HttpResponse
from ninja import NinjaAPI, Schema
from render.packet_html import render_packet

from ai.factory import make_parser
from ai.guards import CallBudget

from .chat_core import route
from .mcp_client import ToolError, call_tool

api = NinjaAPI(urls_namespace="chat-api", docs_url=None)  # no public docs page

_budget = CallBudget(getattr(settings, "AI_DAILY_CALL_LIMIT", 100))
_parser = make_parser()  # offline by default; PAPER_TRAIL_PARSER=bedrock turns on Bedrock
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
    speeches, first = [], None
    for name, arguments in [(action.tool, action.arguments), *action.then]:
        try:
            data = await asyncio.to_thread(call_tool, _client, url, body.token, name, arguments)
        except ToolError as exc:
            if not speeches:
                return api.create_response(
                    request, {"speech": str(exc), "tool": action.tool, "data": None, "pending": None}, status=502)
            speeches.append(f"I could not record the rest: {exc}")
            break
        first = first or data
        speeches.append(data.get("speech") or "Done.")
    return {"speech": " ".join(speeches), "tool": action.tool, "data": first, "pending": None}


class PacketIn(Schema):
    token: str
    room: str | None = None


@api.post("/packet")
async def packet(request, body: PacketIn):
    """The printable evidence packet as one HTML page. The token travels in the body, never the URL."""
    url = getattr(settings, "MCP_URL", "http://127.0.0.1:8000/mcp")
    arguments = {"room": body.room} if body.room else {}
    try:
        data = await asyncio.to_thread(call_tool, _client, url, body.token, "evidence_packet", arguments)
    except ToolError as exc:
        return HttpResponse(str(exc), status=502, content_type="text/plain; charset=utf-8")
    return HttpResponse(render_packet(data), content_type="text/html; charset=utf-8")
