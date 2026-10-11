from datetime import date, timedelta

from engine.recurrence import detect_recurrence
from engine.types import IssueSummary

TODAY = date(2026, 10, 11)


def summary(issue_id, room="bedroom", category="leak", days_ago=1, status="open"):
    return IssueSummary(
        issue_id=issue_id, room=room, category=category, description="x",
        logged_on=TODAY - timedelta(days=days_ago), status=status, updates=0, contacts=0,
        last_contact_on=None, last_contact_method=None, deadline_on=None, deadline_what=None,
        days_until_deadline=None, overdue=False,
    )


def test_three_in_window():
    items = [summary("a", days_ago=62), summary("b", days_ago=31), summary("c", days_ago=2)]
    [r] = detect_recurrence(items, TODAY)
    assert r.count == 3 and r.issue_ids == ("a", "b", "c")
    assert r.first_on == TODAY - timedelta(days=62) and r.latest_on == TODAY - timedelta(days=2)


def test_window_boundary():
    inside = summary("in", days_ago=89)
    outside = summary("out", days_ago=90)
    [r] = detect_recurrence([inside, summary("now", days_ago=0), outside], TODAY, window_days=90)
    assert r.count == 2 and "out" not in r.issue_ids


def test_one_is_not_recurrence():
    assert detect_recurrence([summary("a")], TODAY) == []


def test_room_and_category_keep_groups_apart():
    items = [summary("a"), summary("b", room="kitchen"), summary("c", category="mold")]
    assert detect_recurrence(items, TODAY) == []


def test_resolved_issues_still_count():
    items = [summary("a", days_ago=40, status="resolved"), summary("b", days_ago=3)]
    [r] = detect_recurrence(items, TODAY)
    assert r.count == 2


def test_future_dated_issue_is_ignored():
    items = [summary("a", days_ago=3), summary("b", days_ago=-5)]
    assert detect_recurrence(items, TODAY) == []


def test_most_frequent_first():
    items = [summary("a"), summary("b"), summary("k1", room="kitchen"), summary("k2", room="kitchen"),
             summary("k3", room="kitchen")]
    assert [r.room for r in detect_recurrence(items, TODAY)] == ["kitchen", "bedroom"]
