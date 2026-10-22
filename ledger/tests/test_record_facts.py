from datetime import date

import pytest

from ledger.models import Entry
from ledger.services import log_issue, record_landlord_contact, set_deadline
from ledger.services.record_facts import record_facts

pytestmark = pytest.mark.django_db


def test_facts_come_from_the_record_and_reading_writes_nothing(hh):
    log_issue(household=hh, author="Ibrahim", room="Bedroom", category="leak",
              description="ceiling drips", happened_on="2026-10-01")
    record_landlord_contact(household=hh, author="Ibrahim", method="text", note="told him", room="bedroom")
    set_deadline(household=hh, author="Ibrahim", deadline="2026-10-03", what="fix the ceiling", room="bedroom")
    before = Entry.objects.filter(household=hh).count()
    facts = record_facts(hh, today=date(2026, 10, 11))
    issue = facts["open_issues"][0]
    assert issue["room"] == "bedroom" and issue["days_until_deadline"] == -8
    assert issue["landlord_contacts"][0]["method"] == "text"
    assert issue["deadlines_recorded"][0]["date"] == "2026-10-03"
    assert len(facts["entries"]) == 3
    assert Entry.objects.filter(household=hh).count() == before


def test_each_issue_carries_its_own_counts(hh):
    log_issue(household=hh, author="Ibrahim", room="Bedroom", category="leak", description="ceiling drips")
    record_landlord_contact(household=hh, author="Ibrahim", method="text", note="told him", room="bedroom")
    log_issue(household=hh, author="Ibrahim", room="Kitchen", category="leak", description="sink drips")
    by_room = {i["room"]: i for i in record_facts(hh, today=date(2026, 10, 11))["open_issues"]}
    assert by_room["bedroom"]["landlord_contact_count"] == 1
    assert by_room["kitchen"]["landlord_contact_count"] == 0
