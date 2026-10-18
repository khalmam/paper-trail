import json

from api import endpoints
from api.mcp_client import ToolError

DATA = {"generated_on": "2026-10-17", "notice": "Not legal advice.", "issues": [],
        "integrity": {"ok": True, "verified": 4, "bad_seq": None, "reason": None},
        "head_hash": "abc123", "entry_count": 4, "speech": "ok"}


def post(client, **body):
    return client.post("/api/packet", data=json.dumps(body), content_type="application/json")


def test_packet_endpoint_returns_the_printable_page(client, monkeypatch):
    seen = {}

    def fake(http, url, token, name, arguments):
        seen.update(token=token, name=name)
        return DATA

    monkeypatch.setattr(endpoints, "call_tool", fake)
    response = post(client, token="tok")
    assert response.status_code == 200 and response["content-type"].startswith("text/html")
    assert "Record check passed" in response.content.decode()
    assert seen == {"token": "tok", "name": "evidence_packet"}


def test_bad_token_is_a_502_with_a_plain_message(client, monkeypatch):
    def boom(*args):
        raise ToolError("That access token is not recognized.")

    monkeypatch.setattr(endpoints, "call_tool", boom)
    response = post(client, token="bad")
    assert response.status_code == 502 and b"not recognized" in response.content


def test_token_is_required(client):
    assert post(client).status_code == 422


def test_simulator_can_show_the_packet(client):
    html = client.get("/simulator").content.decode()
    assert "/api/packet" in html and "sandbox" in html
