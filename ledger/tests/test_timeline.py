import pytest

from ledger.exceptions import NoSuchIssue
from ledger.services import add_update, correct_entry, issue_timeline, log_issue

pytestmark = pytest.mark.django_db


def leak(hh, room):
    return log_issue(household=hh, author="a", room=room, category="leak", description="drip")


def test_timeline_follows_one_issue_in_order(hh):
    leak(hh, "Bedroom")
    leak(hh, "Kitchen")
    add_update(household=hh, author="a", note="worse", room="bedroom")
    tl = issue_timeline(hh, "bedroom")
    assert [i.seq for i in tl.items] == [1, 3] and tl.room == "bedroom"


def test_corrections_are_shown_and_flagged(hh):
    first = leak(hh, "Bedroom")
    leak(hh, "Kitchen")
    add_update(household=hh, author="a", note="worse", room="bedroom")
    correct_entry(household=hh, author="a", seq=first.seq, field="description", new_value="steady drip")
    tl = issue_timeline(hh, "bedroom")
    assert [i.seq for i in tl.items] == [1, 3, 4]
    assert tl.items[0].corrected and "steady drip" in tl.items[0].text
    assert tl.items[2].kind == "correction"


def test_timeline_with_no_issue_raises(hh):
    with pytest.raises(NoSuchIssue):
        issue_timeline(hh)
