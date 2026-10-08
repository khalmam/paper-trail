from datetime import date

from ledger.domain.vocab import CONTACT_METHODS
from ledger.models import Entry, Household

from .append import append_entry
from .lookup import find_issue


def record_landlord_contact(*, household: Household, author: str, method: str, note: str,
                            room: str | None = None, contacted_on: str | None = None) -> Entry:
    if method not in CONTACT_METHODS:
        raise ValueError(f"method must be one of {CONTACT_METHODS}")
    if contacted_on:
        date.fromisoformat(contacted_on)  # raises ValueError on bad input
    issue = find_issue(household, room)
    return append_entry(
        household=household, author=author, kind=Entry.Kind.LANDLORD_CONTACT,
        issue_id=issue.issue_id,
        payload={
            "method": method,
            "note": note.strip(),
            "room": issue.payload.get("room"),
            "contacted_on": contacted_on or date.today().isoformat(),
        },
    )
