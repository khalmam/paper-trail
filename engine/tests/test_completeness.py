from dataclasses import replace
from datetime import date

from engine.completeness import score_completeness
from engine.types import IssueSummary

BASE = IssueSummary(
    issue_id="A", room="bedroom", category="leak", description="x", logged_on=date(2026, 10, 1),
    status="open", updates=0, contacts=0, last_contact_on=None, last_contact_method=None,
    deadline_on=None, deadline_what=None, days_until_deadline=None, overdue=False,
)


def test_fresh_issue_is_forty_percent():
    c = score_completeness(BASE)
    assert c.percent == 40 and c.missing == ("photo", "witness", "landlord_contact")


def test_each_item_raises_the_score():
    assert score_completeness(replace(BASE, photo_refs=1)).percent == 60
    assert score_completeness(replace(BASE, photo_refs=1, witnesses=1)).percent == 80
    full = score_completeness(replace(BASE, photo_refs=1, witnesses=1, contacts=2))
    assert full.percent == 100 and full.missing == () and full.next_suggestion() is None


def test_suggestion_names_first_missing_item():
    assert "photo" in score_completeness(BASE).next_suggestion()


def test_suggestion_can_skip_an_item_the_next_step_already_covers():
    c = score_completeness(replace(BASE, photo_refs=1, witnesses=1))
    assert c.missing == ("landlord_contact",)
    assert c.next_suggestion(skip=("landlord_contact",)) is None
    first = score_completeness(BASE).next_suggestion(skip=("photo",))
    assert "witness" in first or "someone" in first
