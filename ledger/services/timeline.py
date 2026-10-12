from engine.timeline import Timeline, build_timeline
from engine.types import EntryView
from ledger.models import Entry, Household

from .lookup import find_issue


def issue_timeline(household: Household, room: str | None = None) -> Timeline:
    """History of the latest issue (in `room` if given), corrections applied."""
    issue = find_issue(household, room)
    views = [
        EntryView(seq=e.seq, kind=e.kind, issue_id=str(e.issue_id), author=e.author,
                  created_at=e.created_at, payload=e.payload)
        for e in Entry.objects.filter(household=household, issue_id=issue.issue_id).order_by("seq")
    ]
    return build_timeline(views, str(issue.issue_id))
