from dataclasses import replace
from datetime import date

from engine.escalation import next_step
from engine.types import IssueSummary

BASE = IssueSummary(
    issue_id="A", room="bedroom", category="leak", description="x", logged_on=date(2026, 10, 1),
    status="open", updates=0, contacts=0, last_contact_on=None, last_contact_method=None,
    deadline_on=None, deadline_what=None, days_until_deadline=None, overdue=False,
)


def with_deadline(days_left, **kw):
    return replace(BASE, contacts=1, deadline_on=date(2026, 10, 20), days_until_deadline=days_left,
                   overdue=days_left < 0, **kw)


def test_ladder_in_order():
    assert next_step(BASE).action == "contact_landlord"
    assert next_step(replace(BASE, contacts=1)).action == "set_deadline"
    assert next_step(with_deadline(5)).action == "wait"
    assert next_step(with_deadline(-3)).action == "reminder"
    assert next_step(with_deadline(-7)).action == "letter"
    assert next_step(with_deadline(-9, letters_sent=1)).action == "packet"


def test_resolved_needs_nothing():
    assert next_step(replace(with_deadline(-30), status="resolved", overdue=False)).action == "none"


def test_threshold_is_a_parameter():
    assert next_step(with_deadline(-3), letter_after_days=3).action == "letter"


def test_wording_never_claims_a_legal_right():
    text = next_step(with_deadline(-20)).message.lower()
    assert "legal" not in text and "entitled" not in text and "must" not in text
