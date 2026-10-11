from datetime import date, datetime, timezone

from engine import kinds
from engine.summary import summarize_issues, urgency_key
from engine.types import EntryView

TODAY = date(2026, 10, 11)


def entry(seq, kind, issue, **payload):
    return EntryView(seq, kind, issue, "a", datetime(2026, 10, 1, tzinfo=timezone.utc), payload)


def opener(seq, issue, room="bedroom", when="2026-10-01"):
    return entry(seq, kinds.ISSUE_LOGGED, issue, room=room, category="leak", description="drip", happened_on=when)


def test_open_issue_with_no_deadline():
    [s] = summarize_issues([opener(1, "A")], TODAY)
    assert s.status == "open" and s.deadline_on is None and not s.overdue


def test_overdue_and_days_left():
    entries = [opener(1, "A"), entry(2, kinds.DEADLINE_SET, "A", deadline_date="2026-10-08", what="fix")]
    [s] = summarize_issues(entries, TODAY)
    assert s.overdue and s.days_until_deadline == -3
    entries[1] = entry(2, kinds.DEADLINE_SET, "A", deadline_date="2026-10-14", what="fix")
    [s] = summarize_issues(entries, TODAY)
    assert not s.overdue and s.days_until_deadline == 3


def test_latest_deadline_wins():
    entries = [
        opener(1, "A"),
        entry(2, kinds.DEADLINE_SET, "A", deadline_date="2026-10-05", what="fix"),
        entry(3, kinds.DEADLINE_SET, "A", deadline_date="2026-10-20", what="fix"),
    ]
    [s] = summarize_issues(entries, TODAY)
    assert s.deadline_on == date(2026, 10, 20) and not s.overdue


def test_resolved_is_never_overdue():
    entries = [
        opener(1, "A"),
        entry(2, kinds.DEADLINE_SET, "A", deadline_date="2026-10-05", what="fix"),
        entry(3, kinds.RESOLVED, "A", note="fixed"),
    ]
    [s] = summarize_issues(entries, TODAY)
    assert s.status == "resolved" and not s.overdue


def test_contacts_and_updates_counted():
    entries = [
        opener(1, "A"),
        entry(2, kinds.LANDLORD_CONTACT, "A", method="text", contacted_on="2026-10-02"),
        entry(3, kinds.LANDLORD_CONTACT, "A", method="call", contacted_on="2026-10-06"),
        entry(4, kinds.UPDATE, "A", note="worse"),
    ]
    [s] = summarize_issues(entries, TODAY)
    assert (s.contacts, s.updates, s.last_contact_method) == (2, 1, "call")
    assert s.last_contact_on == date(2026, 10, 6)


def test_orphan_entries_ignored_and_issues_kept_apart():
    entries = [entry(1, kinds.UPDATE, "ghost", note="?"), opener(2, "A"), opener(3, "B", room="kitchen")]
    summaries = summarize_issues(entries, TODAY)
    assert [s.issue_id for s in summaries] == ["A", "B"]


def test_urgency_order():
    entries = [
        opener(1, "none"),
        opener(2, "soon"), entry(3, kinds.DEADLINE_SET, "soon", deadline_date="2026-10-13", what="x"),
        opener(4, "late"), entry(5, kinds.DEADLINE_SET, "late", deadline_date="2026-10-01", what="x"),
    ]
    ordered = sorted(summarize_issues(entries, TODAY), key=urgency_key)
    assert [s.issue_id for s in ordered] == ["late", "soon", "none"]
