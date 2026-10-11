from datetime import date

import pytest

from ledger.services import log_issue, overview, resolve_issue

pytestmark = pytest.mark.django_db
TODAY = date(2026, 10, 11)


def leak(hh, when, room="Bedroom"):
    return log_issue(household=hh, author="a", room=room, category="leak", description="drip", happened_on=when)


def test_recurrence_counts_resolved_and_open(hh):
    leak(hh, "2026-08-10")
    leak(hh, "2026-09-10")
    resolve_issue(household=hh, author="a", room="bedroom")  # resolves the Sep 10 one
    leak(hh, "2026-10-09")
    leak(hh, "2026-10-01", room="Kitchen")
    result = overview(hh, today=TODAY)
    assert len(result.open) == 3
    [rec] = result.recurrences
    assert (rec.room, rec.count) == ("bedroom", 3)


def test_old_issue_falls_out_of_window(hh):
    leak(hh, "2026-06-01")
    leak(hh, "2026-10-09")
    assert overview(hh, today=TODAY).recurrences == []
