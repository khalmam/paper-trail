from datetime import date

import pytest

from ledger.services import log_issue, open_issues, resolve_issue, set_deadline

pytestmark = pytest.mark.django_db


def test_open_issues_orders_by_urgency_and_hides_resolved(hh):
    log_issue(household=hh, author="a", room="Kitchen", category="pests", description="ants")
    log_issue(household=hh, author="a", room="Bedroom", category="leak", description="drip")
    set_deadline(household=hh, author="a", deadline="2026-10-01", what="fix", room="bedroom")
    log_issue(household=hh, author="a", room="Bathroom", category="mold", description="spots")
    resolve_issue(household=hh, author="a", room="bathroom")
    items = open_issues(hh, today=date(2026, 10, 11))
    assert [i.room for i in items] == ["bedroom", "kitchen"]
    assert items[0].overdue and items[0].days_until_deadline == -10
