import pytest

from ledger.exceptions import NoSuchIssue
from ledger.services import log_issue, record_landlord_contact

pytestmark = pytest.mark.django_db


def issue(hh, room="Bedroom"):
    return log_issue(household=hh, author="a", room=room, category="leak", description="drip")


def test_contact_attaches_to_issue(hh):
    i = issue(hh)
    c = record_landlord_contact(household=hh, author="a", method="text", note="no reply", room="bedroom")
    assert c.issue_id == i.issue_id and c.kind == "landlord_contact"
    assert c.payload["method"] == "text"


def test_contact_validates_input(hh):
    issue(hh)
    with pytest.raises(ValueError):
        record_landlord_contact(household=hh, author="a", method="pigeon", note="x")
    with pytest.raises(ValueError):
        record_landlord_contact(household=hh, author="a", method="call", note="x", contacted_on="last week")


def test_contact_without_issue_raises(hh):
    with pytest.raises(NoSuchIssue):
        record_landlord_contact(household=hh, author="a", method="call", note="x")
