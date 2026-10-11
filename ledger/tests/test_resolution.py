import pytest

from ledger.exceptions import NoSuchIssue
from ledger.services import log_issue, resolve_issue

pytestmark = pytest.mark.django_db


def leak(hh, room="Bedroom"):
    return log_issue(household=hh, author="a", room=room, category="leak", description="drip")


def test_resolves_latest_open_then_the_one_before(hh):
    first, second = leak(hh), leak(hh)
    r1 = resolve_issue(household=hh, author="a", room="bedroom", note="plumber came")
    assert r1.issue_id == second.issue_id and r1.kind == "resolved"
    r2 = resolve_issue(household=hh, author="a", room="bedroom")
    assert r2.issue_id == first.issue_id


def test_nothing_left_to_resolve_raises(hh):
    leak(hh)
    resolve_issue(household=hh, author="a")
    with pytest.raises(NoSuchIssue):
        resolve_issue(household=hh, author="a")


def test_resolve_with_no_issue_raises(hh):
    with pytest.raises(NoSuchIssue):
        resolve_issue(household=hh, author="a")
