from ledger.models import Entry, Household

from .append import append_entry
from .lookup import find_issue


def add_update(*, household: Household, author: str, note: str, room: str | None = None) -> Entry:
    """Attach a note to the most recent logged issue (in `room` if given)."""
    issue = find_issue(household, room)
    return append_entry(
        household=household, author=author, kind=Entry.Kind.UPDATE, issue_id=issue.issue_id,
        payload={"note": note.strip(), "room": issue.payload.get("room")},
    )
