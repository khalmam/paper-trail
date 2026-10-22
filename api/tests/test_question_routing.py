from datetime import date

from ai.guards import CallBudget
from ai.interface import ParsedIssue
from api.chat_core import route

TODAY = date(2026, 10, 15)


class Stub:
    def __init__(self, room="bedroom"):
        self.room, self.calls = room, 0

    def parse_issue(self, utterance, today):
        self.calls += 1
        return ParsedIssue(self.room, "leak", utterance, None, None)


def go(message, parser, pending=None):
    return route(message, TODAY, parser, CallBudget(10), pending)


def test_questions_go_to_the_read_only_path_and_skip_the_parser():
    parser = Stub()
    for text in ("when did I first tell the landlord?", "which problem has the most contacts",
                 "did Amina and I disagree about anything", "list the issues"):
        action = go(text, parser)
        assert action.tool == "record_facts" and action.ask == text, text
    assert parser.calls == 0


def test_reports_requests_and_answers_to_our_question_are_not_captured():
    assert go("there is a leak in the kitchen sink", Stub()).tool == "log_issue"
    assert go("can you log a leak in the kitchen?", Stub()).ask is None
    assert go("the kitchen?", Stub(room=None), pending={"utterance": "leak", "asked": "room"}).ask is None
