from datetime import date

from ai.interface import ParsedIssue
from ai.validate import is_placeholder, parse_checked

TODAY = date(2026, 10, 22)


class Stub:
    def __init__(self, room, description="drips"):
        self.room, self.description = room, description

    def parse_issue(self, utterance, today):
        return ParsedIssue(self.room, "leak", self.description, None, None)


def test_placeholder_text_is_missing_not_an_answer():
    for junk in ("<unknown>", "<UNKNOWN>", "unknown", "N/A", "none", "[none]", "  ", None):
        assert is_placeholder(junk), junk
    assert not is_placeholder("kitchen") and not is_placeholder("ceiling drips")


def test_a_placeholder_room_makes_the_assistant_ask_which_room():
    parsed = parse_checked(Stub("<unknown>"), "lets log a new issue", TODAY)
    assert parsed.room is None and parsed.question == "Which room is it in?"


def test_a_placeholder_description_becomes_empty_so_the_persons_words_are_used():
    assert parse_checked(Stub("garage", "<UNKNOWN>"), "water in the garage", TODAY).description == ""
