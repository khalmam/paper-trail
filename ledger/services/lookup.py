from ledger.exceptions import NoSuchIssue
from ledger.models import Entry, Household


def find_issue(household: Household, room: str | None = None) -> Entry:
    """The most recent logged issue, limited to `room` when given."""
    issues = Entry.objects.filter(household=household, kind=Entry.Kind.ISSUE_LOGGED)
    if room:
        issues = issues.filter(payload__room=room.strip().lower())
    issue = issues.order_by("-seq").first()
    if issue is None:
        where = f" in the {room}" if room else ""
        raise NoSuchIssue(f"There is no logged issue{where} yet.")
    return issue
