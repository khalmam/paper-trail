from datetime import date

from ai.guards import CallBudget
from ai.interface import ParsedIssue
from api.chat_core import MAX_CHARS, route

TODAY = date(2026, 10, 15)


class Stub:
    """Returns a fixed parse and counts calls."""
    def __init__(self, room="bedroom", category="leak"):
        self.room, self.category, self.calls = room, category, 0

    def parse_issue(self, utterance, today):
        self.calls += 1
        return ParsedIssue(self.room, self.category, utterance, None, None)


def go(message, parser=None, limit=10, pending=None):
    return route(message, TODAY, parser or Stub(), CallBudget(limit), pending)


def test_questions_about_the_record_skip_the_parser():
    parser = Stub()
    assert go("what's open?", parser).tool == "whats_open"
    assert go("give me the packet", parser).tool == "evidence_packet"
    assert go("is my record intact", parser).tool == "verify_integrity"
    assert parser.calls == 0


def test_complete_report_becomes_a_log_issue_call():
    action = go("leak in the bedroom ceiling")
    assert action.tool == "log_issue"
    assert action.arguments["room"] == "bedroom" and action.arguments["category"] == "leak"
    assert "happened_on" not in action.arguments


def test_missing_room_asks_and_remembers_the_sentence():
    action = go("something is dripping", Stub(room=None))
    assert action.tool is None and "room" in action.reply.lower()
    assert action.pending == {"utterance": "something is dripping", "asked": "room"}


def test_follow_up_is_parsed_together_with_the_first_message():
    parser = Stub()
    action = go("the bedroom", parser, pending={"utterance": "something is dripping"})
    assert action.tool == "log_issue"
    assert action.arguments["description"] == "something is dripping the bedroom"


def test_daily_limit_blocks_the_parser_and_says_so():
    parser = Stub()
    action = go("leak in the kitchen", parser, limit=0)
    assert action.tool is None and "daily" in action.reply.lower()
    assert parser.calls == 0


def test_empty_message_and_long_message():
    assert "Tell me" in go("   ").reply
    assert len(go("leak " * 500).arguments["description"]) <= MAX_CHARS


def test_a_short_reply_to_the_room_question_is_taken_as_the_room():
    pending = {"utterance": "the air condition is not working", "asked": "room"}
    action = go("in my room 2", Stub(room=None), pending=pending)
    assert action.tool == "log_issue" and action.arguments["room"] == "room 2"


def test_a_reply_naming_a_category_answers_the_category_question():
    pending = {"utterance": "the socket is humming", "asked": "category"}
    action = go("electrical", Stub(room="kitchen", category=None), pending=pending)
    assert action.tool == "log_issue" and action.arguments["category"] == "electrical"


class Multi:
    def parse_issue(self, utterance, today):
        return ParsedIssue("bedroom", "leak", utterance, None, None, contact_method="text",
                           contacted_on="2026-10-14", deadline_on="2026-10-23", deadline_what="fix the ceiling")


def test_one_sentence_becomes_issue_then_contact_then_deadline():
    action = go("leak again, I texted him yesterday and he promised Friday", Multi())
    assert action.tool == "log_issue"
    assert [name for name, _ in action.then] == ["record_landlord_contact", "set_deadline"]
    assert action.then[0][1]["room"] == "bedroom" and action.then[1][1]["deadline"] == "2026-10-16"  # next Friday after Thu 2026-10-15, computed by code


def test_a_plain_report_has_no_follow_up_calls():
    assert go("leak in the bedroom").then == ()


def test_letter_phrases_route_to_the_letter_tools():
    parser = Stub()
    assert go("draft a letter to my landlord", parser).tool == "draft_letter"
    assert go("can you write the letter", parser).tool == "draft_letter"
    assert go("I sent the letter", parser).tool == "confirm_letter_sent"
    assert go("the letter was sent yesterday", parser).tool == "confirm_letter_sent"
    assert parser.calls == 0


def test_talking_about_a_letter_does_not_write_anything_by_accident():
    assert go("should I send a letter?", Stub()).tool != "confirm_letter_sent"


def test_only_a_clear_statement_that_the_letter_was_sent_writes_to_the_record():
    parser = Stub()
    for text in ("my neighbour sent a note about the leak and I told the landlord about it",
                 "should I send a letter?", "I wrote down the date the letter from the council came",
                 "he sent it back unfixed"):
        assert go(text, parser).tool != "confirm_letter_sent", text
    assert go("I sent the letter yesterday", parser).tool == "confirm_letter_sent"
