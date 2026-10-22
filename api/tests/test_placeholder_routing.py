from datetime import date

from ai.guards import CallBudget
from ai.interface import ParsedIssue
from api.chat_core import route


class Stub:
    def parse_issue(self, utterance, today):
        return ParsedIssue("<unknown>", "leak", "<UNKNOWN>", None, None)


def test_a_vague_report_gets_a_question_not_an_error():
    action = route("lets log a new issue", date(2026, 10, 22), Stub(), CallBudget(5))
    assert action.tool is None and "room" in action.reply.lower()
    assert action.pending == {"utterance": "lets log a new issue", "asked": "room"}
