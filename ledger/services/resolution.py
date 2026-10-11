from ledger.models import Entry, Household

from .append import append_entry
from .lookup import find_open_issue


def resolve_issue(*, household: Household, author: str, note: str = "", room: str | None = None) -> Entry:
    """Mark the latest open issue (in `room` if given) as fixed. Corrections are new entries,
    so a resolved issue is never edited; it simply stops counting as open."""
    issue = find_open_issue(household, room)
    return append_entry(
        household=household, author=author, kind=Entry.Kind.RESOLVED, issue_id=issue.issue_id,
        payload={"note": note.strip(), "room": issue.payload.get("room")},
    )
