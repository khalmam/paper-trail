from datetime import date

from django.utils import timezone

from engine.summary import summarize_issues, urgency_key
from engine.types import EntryView, IssueSummary
from ledger.models import Entry, Household


def open_issues(household: Household, today: date | None = None) -> list[IssueSummary]:
    """Open issues, most urgent first. `today` defaults to the current UTC date."""
    today = today or timezone.now().date()
    views = [
        EntryView(seq=e.seq, kind=e.kind, issue_id=str(e.issue_id), author=e.author,
                  created_at=e.created_at, payload=e.payload)
        for e in Entry.objects.filter(household=household).order_by("seq").iterator()
    ]
    open_ones = [s for s in summarize_issues(views, today) if s.status == "open"]
    return sorted(open_ones, key=urgency_key)
