from ledger.exceptions import NoSuchIssue
from ledger.models import Entry, Household

from .append import append_entry


def add_update(*, household: Household, author: str, note: str, room: str | None = None) -> Entry:
    """Attach a note to the most recent logged issue (in `room` if given)."""
    issues = Entry.objects.filter(household=household, kind=Entry.Kind.ISSUE_LOGGED)
    if room:
        issues = issues.filter(payload__room=room.strip().lower())
    issue = issues.order_by("-seq").first()
    if issue is None:
        where = f" in the {room}" if room else ""
        raise NoSuchIssue(f"There is no logged issue{where} to add to.")
    return append_entry(
        household=household, author=author, kind=Entry.Kind.UPDATE, issue_id=issue.issue_id,
        payload={"note": note.strip(), "room": issue.payload.get("room")},
    )
