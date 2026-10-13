from datetime import datetime, timezone

from engine import kinds
from engine.conflicts import detect_conflicts
from engine.types import EntryView

T = datetime(2026, 10, 1, 9, tzinfo=timezone.utc)


def e(seq, kind, issue, author, **payload):
    return EntryView(seq, kind, issue, author, T, payload)


def opener(seq, issue, author, room="bedroom", category="leak", when="2026-10-01"):
    return e(seq, kinds.ISSUE_LOGGED, issue, author, room=room, category=category,
             description="x", happened_on=when)


def deadline(seq, issue, author, day):
    return e(seq, kinds.DEADLINE_SET, issue, author, deadline_date=day, what="fix")


def fix(seq, issue, author, target, field, new):
    return e(seq, kinds.CORRECTION, issue, author, corrects_seq=target, field=field, new_value=new)


def kinds_of(entries):
    return [c.kind for c in detect_conflicts(entries)]


def test_clean_log_has_no_conflicts():
    assert detect_conflicts([opener(1, "A", "Ibrahim"), deadline(2, "A", "Ibrahim", "2026-10-10")]) == []


def test_different_deadlines_by_different_people():
    entries = [opener(1, "A", "Ibrahim"), deadline(2, "A", "Ibrahim", "2026-10-10"),
               deadline(3, "A", "Amina", "2026-10-15")]
    [c] = detect_conflicts(entries)
    assert c.kind == "deadline_differs" and c.authors == ("Amina", "Ibrahim")
    assert "Amina and Ibrahim recorded different deadlines for the bedroom leak" in c.message


def test_same_person_changing_or_same_date_is_not_a_conflict():
    own = [opener(1, "A", "Ibrahim"), deadline(2, "A", "Ibrahim", "2026-10-10"), deadline(3, "A", "Ibrahim", "2026-10-15")]
    same = [opener(1, "A", "Ibrahim"), deadline(2, "A", "Ibrahim", "2026-10-10"), deadline(3, "A", "Amina", "2026-10-10")]
    assert kinds_of(own) == [] and kinds_of(same) == []


def test_reopened_after_fix():
    entries = [opener(1, "A", "Ibrahim"), e(2, kinds.RESOLVED, "A", "Ibrahim"),
               e(3, kinds.UPDATE, "A", "Amina", note="still dripping")]
    [c] = detect_conflicts(entries)
    assert c.kind == "reopened_after_fix" and "Ibrahim marked the bedroom leak as fixed, but Amina" in c.message


def test_resolver_adding_more_or_update_before_fix_is_fine():
    own_later = [opener(1, "A", "Ibrahim"), e(2, kinds.RESOLVED, "A", "Ibrahim"), e(3, kinds.UPDATE, "A", "Ibrahim", note="x")]
    before = [opener(1, "A", "Ibrahim"), e(2, kinds.UPDATE, "A", "Amina", note="x"), e(3, kinds.RESOLVED, "A", "Ibrahim")]
    assert kinds_of(own_later) == [] and kinds_of(before) == []


def test_correction_dispute_needs_two_people_and_two_values():
    base = [opener(1, "A", "Ibrahim")]
    assert kinds_of(base + [fix(2, "A", "Ibrahim", 1, "room", "kitchen"), fix(3, "A", "Amina", 1, "room", "hallway")]) \
        == ["correction_dispute"]
    assert kinds_of(base + [fix(2, "A", "Ibrahim", 1, "room", "kitchen"), fix(3, "A", "Ibrahim", 1, "room", "hallway")]) == []


def test_similar_reports_by_different_people():
    [c] = detect_conflicts([opener(1, "A", "Ibrahim", when="2026-10-01"), opener(2, "B", "Amina", when="2026-10-03")])
    assert c.kind == "similar_reports" and "2 days apart" in c.message and c.issue_id == "B"


def test_similar_reports_boundaries():
    def pair(**second):
        args = dict(room="bedroom", category="leak", when="2026-10-03", author="Amina") | second
        return [opener(1, "A", "Ibrahim", when="2026-10-01"),
                opener(2, "B", args["author"], args["room"], args["category"], args["when"])]
    assert kinds_of(pair(when="2026-10-01")) == []          # same date: they agree
    assert kinds_of(pair(when="2026-10-06")) == []          # 5 days apart: separate events
    assert kinds_of(pair(author="Ibrahim")) == []           # same person
    assert kinds_of(pair(room="kitchen")) == []
    assert kinds_of(pair(category="mold")) == []


def test_corrected_dates_are_used_for_similar_reports():
    entries = [opener(1, "A", "Ibrahim", when="2026-10-01"), opener(2, "B", "Amina", when="2026-10-09"),
               fix(3, "B", "Amina", 2, "happened_on", "2026-10-03")]
    assert kinds_of(entries) == ["similar_reports"]


def test_wording_never_accuses_anyone():
    entries = [opener(1, "A", "Ibrahim", when="2026-10-01"), opener(2, "B", "Amina", when="2026-10-03"),
               deadline(3, "A", "Ibrahim", "2026-10-10"), deadline(4, "A", "Amina", "2026-10-15"),
               e(5, kinds.RESOLVED, "A", "Ibrahim"), e(6, kinds.UPDATE, "A", "Amina", note="x")]
    text = " ".join(c.message.lower() for c in detect_conflicts(entries))
    assert len(detect_conflicts(entries)) >= 3
    for word in ("lie", "lying", "false", "wrong", "fault", "blame", "must"):
        assert word not in text
