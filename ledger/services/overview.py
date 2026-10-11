from dataclasses import dataclass
from datetime import date

from django.conf import settings
from django.utils import timezone

from engine.recurrence import Recurrence, detect_recurrence
from engine.summary import summarize_issues, urgency_key
from engine.types import EntryView, IssueSummary
from ledger.models import Entry, Household


@dataclass(frozen=True)
class Overview:
    open: list[IssueSummary]            # unresolved issues, most urgent first
    recurrences: list[Recurrence]       # repeated room+category problems in the window


def overview(household: Household, today: date | None = None) -> Overview:
    """One database read, then pure engine rules. `today` defaults to the UTC date."""
    today = today or timezone.now().date()
    views = [
        EntryView(seq=e.seq, kind=e.kind, issue_id=str(e.issue_id), author=e.author,
                  created_at=e.created_at, payload=e.payload)
        for e in Entry.objects.filter(household=household).order_by("seq").iterator()
    ]
    summaries = summarize_issues(views, today)
    return Overview(
        open=sorted((s for s in summaries if s.status == "open"), key=urgency_key),
        recurrences=detect_recurrence(summaries, today, settings.RECURRENCE_WINDOW_DAYS),
    )


def open_issues(household: Household, today: date | None = None) -> list[IssueSummary]:
    return overview(household, today).open
