import json

from api import endpoints
from api.mcp_client import ToolError


def post(client, **body):
    return client.post("/api/chat", data=json.dumps(body), content_type="application/json")


def test_complete_report_calls_log_issue_with_the_token(client, monkeypatch):
    seen = {}

    def fake_call(http, url, token, name, arguments):
        seen.update(token=token, name=name, arguments=arguments)
        return {"speech": "Logged. That's entry 1 in your evidence log."}

    monkeypatch.setattr(endpoints, "call_tool", fake_call)
    response = post(client, message="leak in the bedroom ceiling", token="tok")
    assert response.status_code == 200
    assert response.json()["speech"].startswith("Logged")
    assert seen["token"] == "tok" and seen["name"] == "log_issue"
    assert seen["arguments"]["room"] == "bedroom"


def test_missing_detail_asks_a_question_and_calls_no_tool(client, monkeypatch):
    monkeypatch.setattr(endpoints, "call_tool", lambda *a: (_ for _ in ()).throw(AssertionError("no tool call")))
    body = post(client, message="something is dripping", token="tok").json()
    assert "room" in body["speech"].lower() and body["pending"] == {"utterance": "something is dripping", "asked": "room"}


def test_record_questions_route_to_their_tool(client, monkeypatch):
    monkeypatch.setattr(endpoints, "call_tool", lambda http, url, token, name, args: {"speech": name})
    assert post(client, message="what's open?", token="t").json()["speech"] == "whats_open"


def test_tool_failure_is_a_502_with_a_readable_message(client, monkeypatch):
    def boom(*args):
        raise ToolError("That access token is not recognized.")

    monkeypatch.setattr(endpoints, "call_tool", boom)
    response = post(client, message="what's open?", token="bad")
    assert response.status_code == 502 and "not recognized" in response.json()["speech"]


def test_token_is_required(client):
    assert post(client, message="hello").status_code == 422
