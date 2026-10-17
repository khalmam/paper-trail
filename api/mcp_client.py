"""Calls our own /mcp endpoint like any other MCP client would. Pure HTTP, no Django."""
import json

import httpx


class ToolError(RuntimeError):
    pass


def _message(response: httpx.Response) -> dict:
    if "text/event-stream" in response.headers.get("content-type", ""):
        data = [line[5:].strip() for line in response.text.splitlines() if line.startswith("data:")]
        if not data:
            raise ToolError("The tool server sent an empty reply.")
        return json.loads(data[-1])
    return response.json()


def call_tool(client: httpx.Client, url: str, token: str, name: str, arguments: dict) -> dict:
    body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": name, "arguments": arguments}}
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json, text/event-stream"}
    try:
        response = client.post(url, json=body, headers=headers)
        response.raise_for_status()
        message = _message(response)
    except (httpx.HTTPError, ValueError) as exc:
        raise ToolError("The tool server could not be reached.") from exc
    if "error" in message:
        raise ToolError(message["error"].get("message", "The tool call failed."))
    result = message["result"]
    texts = [b.get("text", "") for b in result.get("content", []) if b.get("type") == "text"]
    if result.get("isError"):
        raise ToolError(" ".join(texts) or "The tool call failed.")
    if isinstance(result.get("structuredContent"), dict):
        return result["structuredContent"]
    for text in texts:
        try:
            parsed = json.loads(text)
        except ValueError:
            continue
        if isinstance(parsed, dict):
            return parsed
    raise ToolError("The tool returned nothing readable.")
