import pytest

from ledger.exceptions import NoSuchIssue
from ledger.services import log_issue, set_deadline

pytestmark = pytest.mark.django_db


def issue(hh):
    return log_issue(household=hh, author="a", room="Bedroom", category="leak", description="drip")


def test_deadline_is_stored_as_given(hh):
    i = issue(hh)
    d = set_deadline(household=hh, author="a", deadline="2026-10-20", what="fix the ceiling")
    assert d.issue_id == i.issue_id and d.payload["deadline_date"] == "2026-10-20"


def test_bad_date_is_rejected(hh):
    issue(hh)
    for bad in ("friday", "2026-13-40", ""):
        with pytest.raises(ValueError):
            set_deadline(household=hh, author="a", deadline=bad, what="x")


def test_deadline_without_issue_raises(hh):
    with pytest.raises(NoSuchIssue):
        set_deadline(household=hh, author="a", deadline="2026-10-20", what="x")
