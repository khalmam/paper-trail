import pytest

from ledger.exceptions import NoSuchIssue
from ledger.services import add_update, log_issue

pytestmark = pytest.mark.django_db


def issue(hh, room):
    return log_issue(household=hh, author="a", room=room, category="leak", description="drip")


def test_update_attaches_to_latest_issue_in_room(hh):
    bedroom, _kitchen = issue(hh, "Bedroom"), issue(hh, "Kitchen")
    update = add_update(household=hh, author="a", note="worse now", room="bedroom")
    assert update.issue_id == bedroom.issue_id and update.seq == 3


def test_update_without_room_uses_latest(hh):
    issue(hh, "Bedroom")
    kitchen = issue(hh, "Kitchen")
    assert add_update(household=hh, author="a", note="more").issue_id == kitchen.issue_id


def test_update_with_no_issue_raises(hh):
    with pytest.raises(NoSuchIssue):
        add_update(household=hh, author="a", note="orphan")


def test_log_issue_validates_input(hh):
    with pytest.raises(ValueError):
        log_issue(household=hh, author="a", room="x", category="dragons", description="d")
    with pytest.raises(ValueError):
        log_issue(household=hh, author="a", room="x", category="leak", description="d", happened_on="yesterday")
