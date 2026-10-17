import json

import httpx
import pytest

from api.mcp_client import ToolError, call_tool

URL = "http://test/mcp"


def client_for(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def rpc(result=None, error=None):
    return {"jsonrpc": "2.0", "id": 1, **({"error": error} if error else {"result": result})}


def test_reads_a_plain_json_reply_and_sends_the_token():
    seen = {}

    def handler(request):
        seen["auth"] = request.headers["authorization"]
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json=rpc({"content": [{"type": "text", "text": json.dumps({"speech": "hi"})}]}))

    out = call_tool(client_for(handler), URL, "tok", "whats_open", {})
    assert out == {"speech": "hi"}
    assert seen["auth"] == "Bearer tok" and seen["body"]["params"]["name"] == "whats_open"


def test_reads_a_server_sent_event_reply():
    event = "event: message\ndata: " + json.dumps(rpc({"structuredContent": {"speech": "ok"}, "content": []})) + "\n\n"
    handler = lambda request: httpx.Response(200, text=event, headers={"content-type": "text/event-stream"})
    assert call_tool(client_for(handler), URL, "t", "log_issue", {"room": "bedroom"}) == {"speech": "ok"}


def test_tool_errors_and_rpc_errors_become_tool_error():
    bad_tool = lambda r: httpx.Response(200, json=rpc({"isError": True, "content": [{"type": "text", "text": "nope"}]}))
    bad_rpc = lambda r: httpx.Response(200, json=rpc(error={"message": "boom"}))
    with pytest.raises(ToolError, match="nope"):
        call_tool(client_for(bad_tool), URL, "t", "x", {})
    with pytest.raises(ToolError, match="boom"):
        call_tool(client_for(bad_rpc), URL, "t", "x", {})


def test_unreachable_server_becomes_tool_error():
    def handler(request):
        raise httpx.ConnectError("down")
    with pytest.raises(ToolError, match="could not be reached"):
        call_tool(client_for(handler), URL, "t", "x", {})
