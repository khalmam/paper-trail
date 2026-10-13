from datetime import date

import pytest

from ledger.services import log_issue, open_issues, resolve_issue, set_deadline
from ledger.services import overview as overview_for

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


def test_guidance_for_each_open_issue(hh):
    from ledger.services import add_update, record_landlord_contact
    log_issue(household=hh, author="a", room="Bedroom", category="leak", description="drip")
    record_landlord_contact(household=hh, author="a", method="text", note="told him")
    add_update(household=hh, author="a", note="photo taken", photo_ref="stain photo")
    result = overview_for(hh)
    [g] = result.guidance.values()
    assert g.completeness.percent == 80 and g.step.action == "set_deadline"


def test_conflicts_surface_in_overview(hh):
    log_issue(household=hh, author="Ibrahim", room="Bedroom", category="leak", description="drip")
    set_deadline(household=hh, author="Ibrahim", deadline="2026-10-10", what="fix", room="bedroom")
    set_deadline(household=hh, author="Amina", deadline="2026-10-15", what="fix", room="bedroom")
    [c] = overview_for(hh, today=date(2026, 10, 11)).conflicts
    assert c.kind == "deadline_differs"
