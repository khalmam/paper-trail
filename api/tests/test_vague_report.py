from datetime import date

from ai.guards import CallBudget
from ai.interface import ParsedIssue
from api.chat_core import route


class Vague:
    def parse_issue(self, utterance, today):
        return ParsedIssue("store", "other", "the store", None, None)


def test_a_vague_report_asks_what_is_wrong_instead_of_sealing_it():
    action = route("lets log a new issue the store", date(2026, 10, 22), Vague(), CallBudget(5))
    assert action.tool is None and "problem" in action.reply.lower()
    assert action.pending["asked"] == "description"
