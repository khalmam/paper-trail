from datetime import date, datetime, timezone

import pytest

from engine import kinds
from engine.letter import PLACEHOLDERS, build_letter
from engine.types import EntryView

TODAY = date(2026, 10, 11)
T = datetime(2026, 10, 1, 9, tzinfo=timezone.utc)


def e(seq, kind, issue, **payload):
    return EntryView(seq, kind, issue, "Ibrahim", T, payload)


def opener(seq, issue, when="2026-10-01", room="bedroom"):
    return e(seq, kinds.ISSUE_LOGGED, issue, room=room, category="leak", description="ceiling drips",
             happened_on=when)


FULL = [
    opener(1, "A"),
    e(2, kinds.LANDLORD_CONTACT, "A", method="text", contacted_on="2026-10-02", note="told him"),
    e(3, kinds.DEADLINE_SET, "A", deadline_date="2026-10-03", what="fix the ceiling"),
]


def test_letter_states_only_what_the_record_holds():
    letter = build_letter(FULL, TODAY, "A")
    body = letter.body
    assert "2026-10-01" in body and "ceiling drips" in body
    assert "by text on 2026-10-02" in body
    assert "2026-10-03" in body and "fix the ceiling" in body and "8 days ago" in body
    assert "bedroom leak" in letter.subject


def test_letter_has_placeholders_and_a_review_note():
    letter = build_letter(FULL, TODAY, "A")
    assert all(p in letter.body for p in PLACEHOLDERS)
    assert "not legal advice" in letter.note.lower()


def test_letter_makes_no_threats_or_legal_claims():
    text = build_letter(FULL, TODAY, "A").body.lower()
    for word in ("sue", "court", "legal action", "illegal", "violation", "breach", "entitled",
                 "withhold", "must", "demand", "guarantee"):
        assert word not in text


def test_no_deadline_means_no_deadline_sentence():
    body = build_letter([opener(1, "A")], TODAY, "A").body
    assert "date set" not in body and "make sure you are aware" in body


def test_repeats_are_mentioned_when_they_exist():
    entries = [opener(1, "A", when="2026-09-20"), opener(2, "B", when="2026-10-05")]
    assert "recorded 2 times" in build_letter(entries, TODAY, "B").body


def test_unknown_or_fixed_problems_raise_a_plain_error():
    with pytest.raises(ValueError, match="no such problem"):
        build_letter(FULL, TODAY, "nope")
    with pytest.raises(ValueError, match="already marked as fixed"):
        build_letter([opener(1, "A"), e(2, kinds.RESOLVED, "A")], TODAY, "A")


def test_letter_is_json_ready():
    import json
    assert json.loads(json.dumps(build_letter(FULL, TODAY, "A").to_dict()))["issue_id"] == "A"
