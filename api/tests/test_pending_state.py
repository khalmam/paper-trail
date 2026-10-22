from datetime import date

from ai.guards import CallBudget
from ai.interface import ParsedIssue
from api.chat_core import route

TODAY = date(2026, 10, 22)
PENDING = {"utterance": "the store", "asked": "description", "room": "store"}


class Shelf:
    def parse_issue(self, utterance, today):
        return ParsedIssue("store", "other", "the shelf has broke", None, None)


def run(text, pending=None):
    return route(text, TODAY, Shelf(), CallBudget(5), pending=pending)


def test_a_greeting_never_starts_a_report():
    a = run("hello")
    assert a.tool is None and a.pending is None


def test_a_question_while_a_report_is_pending_is_answered_and_clears_it():
    a = run("did i tell the landlord?", PENDING)
    assert a.tool == "record_facts" and a.ask and a.pending is None


def test_the_reply_to_the_description_question_becomes_the_description():
    a = run("the shelf has broke", PENDING)
    assert a.tool == "log_issue" and a.arguments["room"] == "store"


def test_cancel_drops_the_pending_report():
    a = run("never mind", PENDING)
    assert a.tool is None and a.pending is None
