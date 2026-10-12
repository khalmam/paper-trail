from datetime import date

import pytest

from ledger.exceptions import NoSuchEntry
from ledger.models import Entry, Household
from ledger.services import correct_entry, log_issue, overview, verify_chain

pytestmark = pytest.mark.django_db


def leak(hh, when="2026-10-01", room="Bedroom"):
    return log_issue(household=hh, author="a", room=room, category="leak", description="drip", happened_on=when)


def fix(hh, seq, field, value, **kw):
    return correct_entry(household=hh, author="a", seq=seq, field=field, new_value=value, **kw)


def test_correction_changes_how_the_log_reads_but_not_the_original(hh):
    e = leak(hh)
    c = fix(hh, e.seq, "happened_on", "2026-10-05", reason="wrong day")
    assert c.kind == "correction" and c.issue_id == e.issue_id
    assert (c.payload["old_value"], c.payload["new_value"]) == ("2026-10-01", "2026-10-05")
    assert Entry.objects.get(pk=e.pk).payload["happened_on"] == "2026-10-01"
    [issue] = overview(hh, today=date(2026, 10, 11)).open
    assert issue.logged_on == date(2026, 10, 5)
    assert verify_chain(hh).ok


def test_second_correction_records_the_first_as_old_value(hh):
    e = leak(hh)
    fix(hh, e.seq, "room", "kitchen")
    second = fix(hh, e.seq, "room", "hallway")
    assert second.payload["old_value"] == "kitchen"


def test_rejections(hh):
    e = leak(hh)
    first = fix(hh, e.seq, "category", "mold")
    with pytest.raises(NoSuchEntry):
        fix(hh, 99, "room", "kitchen")
    with pytest.raises(ValueError):
        fix(hh, e.seq, "method", "text")        # wrong field for this kind of entry
    with pytest.raises(ValueError):
        fix(hh, e.seq, "happened_on", "last week")
    with pytest.raises(ValueError):
        fix(hh, e.seq, "category", "mold")      # already mold: no-op
    with pytest.raises(ValueError):
        fix(hh, first.seq, "note", "x")         # a correction cannot be corrected


def test_cannot_correct_another_households_entry(hh):
    other = Household.objects.create(name="Other")
    theirs = leak(other)
    with pytest.raises(NoSuchEntry):
        fix(hh, theirs.seq, "room", "kitchen")
