import pytest

from ledger.services import log_issue
from ledger.services.ledger_view import ledger_view

pytestmark = pytest.mark.django_db


def test_ledger_view_lists_entries_with_short_hashes_and_integrity(hh):
    log_issue(household=hh, author="Ibrahim", room="Bedroom", category="leak", description="ceiling drips")
    data = ledger_view(hh)
    assert data["integrity"]["ok"] and len(data["entries"]) == 1
    e = data["entries"][0]
    assert e["seq"] == 1 and len(e["hash"]) == 8 and "ceiling drips" in e["summary"]
