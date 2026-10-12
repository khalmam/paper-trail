from datetime import date, timedelta

import pytest

from ai.fake import FakeParser
from ai.interface import ParsedIssue
from ai.validate import enforce_vocab, parse_checked

from .cases import CASES

TODAY = date(2026, 10, 11)


@pytest.mark.parametrize("text,room,category,days_ago,question", CASES)
def test_hand_written_cases(text, room, category, days_ago, question):
    got = parse_checked(FakeParser(), text, TODAY)
    assert (got.room, got.category) == (room, category)
    expected = (TODAY - timedelta(days=days_ago)).isoformat() if days_ago is not None else None
    assert got.happened_on == expected
    if question:
        assert question in got.question
    else:
        assert got.complete


def test_invented_category_cannot_reach_the_ledger():
    got = enforce_vocab(ParsedIssue("Bedroom ", "plumbing", "x"), TODAY)
    assert got.room == "bedroom" and got.category is None and "What kind" in got.question


def test_bad_or_future_dates_are_dropped():
    assert enforce_vocab(ParsedIssue("kitchen", "leak", "x", "tomorrow-ish"), TODAY).happened_on is None
    assert enforce_vocab(ParsedIssue("kitchen", "leak", "x", "2026-12-25"), TODAY).happened_on is None
    assert enforce_vocab(ParsedIssue("kitchen", "leak", "x", "2026-10-01"), TODAY).happened_on == "2026-10-01"
