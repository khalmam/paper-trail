from datetime import date, datetime, timezone

from engine import kinds
from engine.corrections import apply_corrections
from engine.summary import summarize_issues
from engine.timeline import build_timeline
from engine.types import EntryView

TODAY = date(2026, 10, 11)


def entry(seq, kind, issue, **payload):
    return EntryView(seq, kind, issue, "a", datetime(2026, 10, 1, 9, tzinfo=timezone.utc), payload)


def opener(seq=1, issue="A", room="bedroom", when="2026-10-01"):
    return entry(seq, kinds.ISSUE_LOGGED, issue, room=room, category="leak", description="drip", happened_on=when)


def fix(seq, target, field, new, issue="A", old=None, reason=""):
    return entry(seq, kinds.CORRECTION, issue, corrects_seq=target, field=field,
                 old_value=old, new_value=new, reason=reason)


def test_summary_uses_the_corrected_value():
    [s] = summarize_issues([opener(), fix(2, 1, "happened_on", "2026-10-05")], TODAY)
    assert s.logged_on == date(2026, 10, 5)


def test_later_correction_wins():
    entries = [opener(), fix(2, 1, "room", "kitchen"), fix(3, 1, "room", "hallway")]
    [patched] = [e for e in apply_corrections(entries) if e.seq == 1]
    assert patched.payload["room"] == "hallway" and patched.corrected


def test_bad_corrections_are_ignored_and_originals_untouched():
    original = opener()
    entries = [original, fix(2, 99, "room", "x"), fix(3, 2, "room", "x"), fix(4, 1, "", "x")]
    result = apply_corrections(entries)
    assert all(not e.corrected for e in result)
    assert original.payload["room"] == "bedroom"


def test_timeline_flags_corrections_and_uses_corrected_header():
    entries = [
        opener(room="kitchen"),
        fix(2, 1, "room", "bedroom", old="kitchen", reason="wrong room"),
        entry(3, kinds.UPDATE, "other", note="x"),
    ]
    tl = build_timeline(entries, "A")
    assert tl.room == "bedroom" and [i.seq for i in tl.items] == [1, 2]
    assert tl.items[0].corrected and not tl.items[1].corrected
    assert "Corrected room" in tl.items[1].text and "wrong room" in tl.items[1].text
