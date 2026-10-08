import pytest

from ledger.exceptions import NoSuchIssue
from ledger.services import log_issue
from ledger.services.lookup import find_issue

pytestmark = pytest.mark.django_db


def issue(hh, room):
    return log_issue(household=hh, author="a", room=room, category="leak", description="drip")


def test_find_latest_and_by_room(hh):
    bedroom, kitchen = issue(hh, "Bedroom"), issue(hh, "Kitchen")
    assert find_issue(hh).pk == kitchen.pk
    assert find_issue(hh, "  BEDROOM ").pk == bedroom.pk


def test_find_with_nothing_logged_raises(hh):
    with pytest.raises(NoSuchIssue):
        find_issue(hh)
