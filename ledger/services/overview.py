from dataclasses import dataclass
from datetime import date

from django.conf import settings
from django.utils import timezone

from engine.completeness import Completeness, score_completeness
from engine.conflicts import Conflict, detect_conflicts
from engine.escalation import Step, next_step
from engine.recurrence import Recurrence, detect_recurrence
from engine.summary import summarize_issues, urgency_key
from engine.types import EntryView, IssueSummary
from ledger.models import Entry, Household


@dataclass(frozen=True)
class Guidance:
    issue_id: str
    completeness: Completeness
    step: Step

    def to_dict(self) -> dict:
        return {"issue_id": self.issue_id, "completeness": self.completeness.to_dict(),
                "next_step": self.step.to_dict()}


@dataclass(frozen=True)
class Overview:
    open: list[IssueSummary]            # unresolved issues, most urgent first
    recurrences: list[Recurrence]       # repeated room+category problems in the window
    conflicts: list[Conflict]           # places where roommates' records disagree
    guidance: dict[str, Guidance]       # issue_id -> completeness and next step (open issues)


def overview(household: Household, today: date | None = None) -> Overview:
    """One database read, then pure engine rules. `today` defaults to the UTC date."""
    today = today or timezone.now().date()
    views = [
        EntryView(seq=e.seq, kind=e.kind, issue_id=str(e.issue_id), author=e.author,
                  created_at=e.created_at, payload=e.payload)
        for e in Entry.objects.filter(household=household).order_by("seq").iterator()
    ]
    summaries = summarize_issues(views, today)
    open_ones = sorted((s for s in summaries if s.status == "open"), key=urgency_key)
    return Overview(
        open=open_ones,
        recurrences=detect_recurrence(summaries, today, settings.RECURRENCE_WINDOW_DAYS),
        conflicts=detect_conflicts(views),
        guidance={s.issue_id: Guidance(s.issue_id, score_completeness(s), next_step(s)) for s in open_ones},
    )


def open_issues(household: Household, today: date | None = None) -> list[IssueSummary]:
    return overview(household, today).open
