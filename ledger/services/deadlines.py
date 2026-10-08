from datetime import date

from ledger.models import Entry, Household

from .append import append_entry
from .lookup import find_issue


def set_deadline(*, household: Household, author: str, deadline: str, what: str,
                 room: str | None = None) -> Entry:
    """Record a deadline the USER gave. Nothing here ever computes or guesses one."""
    try:
        due = date.fromisoformat(deadline)
    except ValueError:
        raise ValueError("The deadline must be a calendar date like 2026-10-20.") from None
    issue = find_issue(household, room)
    return append_entry(
        household=household, author=author, kind=Entry.Kind.DEADLINE_SET,
        issue_id=issue.issue_id,
        payload={"deadline_date": due.isoformat(), "what": what.strip(), "room": issue.payload.get("room")},
    )
