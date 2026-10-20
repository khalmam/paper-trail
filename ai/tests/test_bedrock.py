from datetime import date

from ai.bedrock import BedrockParser, FallbackParser
from ai.fake import FakeParser
from ai.validate import enforce_vocab

TODAY = date(2026, 10, 17)


class StubClient:
    """Stands in for boto3's bedrock-runtime client."""
    def __init__(self, form=None, error=None):
        self.form, self.error, self.calls = form, error, []

    def converse(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return {"output": {"message": {"content": [{"toolUse": {"input": self.form}}]}}}


FORM = {"room": "Living Room", "category": "heating", "description": "AC not cooling", "happened_on": ""}


def test_form_becomes_a_parsed_issue_and_blank_date_means_today():
    parsed = BedrockParser(StubClient(FORM), "m").parse_issue("the AC is not cooling", TODAY)
    assert (parsed.room, parsed.category, parsed.happened_on) == ("Living Room", "heating", None)
    assert enforce_vocab(parsed, TODAY).complete


def test_request_forces_the_form_and_tells_the_model_the_date():
    client = StubClient(FORM)
    BedrockParser(client, "model-x").parse_issue("x" * 900, TODAY)
    call = client.calls[0]
    assert call["modelId"] == "model-x" and "2026-10-17" in call["system"][0]["text"]
    assert call["toolConfig"]["toolChoice"] == {"tool": {"name": "fill_form"}}
    assert len(call["messages"][0]["content"][0]["text"]) == 500


def test_a_made_up_category_is_rejected_by_the_rules_not_trusted():
    odd = BedrockParser(StubClient({**FORM, "category": "plumbing-ish"}), "m").parse_issue("x", TODAY)
    checked = enforce_vocab(odd, TODAY)
    assert checked.category is None and not checked.complete


def test_failure_falls_back_to_the_offline_parser():
    broken = BedrockParser(StubClient(error=RuntimeError("denied")), "m")
    parsed = FallbackParser(broken, FakeParser()).parse_issue("leak in the bedroom", TODAY)
    assert parsed.room == "bedroom" and parsed.category == "leak"


MULTI = {**FORM, "room": "bedroom", "category": "leak", "contact_method": "text",
         "contact_note": "told him about the leak", "contacted_on": "2026-10-16",
         "deadline_on": "2026-10-23", "deadline_what": "fix the ceiling"}


def test_one_sentence_can_carry_a_contact_and_a_deadline():
    parsed = BedrockParser(StubClient(MULTI), "m").parse_issue("x", TODAY)
    checked = enforce_vocab(parsed, TODAY)
    assert checked.contact_method == "text" and checked.contacted_on == "2026-10-16"
    assert checked.deadline_on == "2026-10-23" and checked.deadline_what == "fix the ceiling"


def test_rules_drop_what_the_model_got_wrong():
    bad = {**MULTI, "contact_method": "carrier pigeon", "deadline_on": "next-ish"}
    checked = enforce_vocab(BedrockParser(StubClient(bad), "m").parse_issue("x", TODAY), TODAY)
    assert checked.contact_method is None and checked.contacted_on is None
    assert checked.deadline_on is None
    future = {**MULTI, "contacted_on": "2026-12-01"}
    assert enforce_vocab(BedrockParser(StubClient(future), "m").parse_issue("x", TODAY), TODAY).contacted_on is None
