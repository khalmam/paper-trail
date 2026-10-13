from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from .completeness import Completeness, score_completeness
from .conflicts import Conflict, detect_conflicts
from .escalation import Step, next_step
from .recurrence import Recurrence, detect_recurrence
from .summary import summarize_issues, urgency_key
from .timeline import Timeline, build_timeline
from .types import EntryView, IssueSummary

NOTICE = (
    "This packet lists what the household reported, taken from a log that shows later changes. "
    "It is not legal advice and it does not decide who is right."
)


@dataclass(frozen=True)
class IssuePacket:
    summary: IssueSummary
    timeline: Timeline
    completeness: Completeness
    next_step: Step
    recurrence: Recurrence | None
    conflicts: tuple[Conflict, ...]

    def to_dict(self) -> dict:
        return {
            "summary": self.summary.to_dict(),
            "timeline": self.timeline.to_dict(),
            "completeness": self.completeness.to_dict(),
            "next_step": self.next_step.to_dict(),
            "recurrence": self.recurrence.to_dict() if self.recurrence else None,
            "conflicts": [c.to_dict() for c in self.conflicts],
        }


@dataclass(frozen=True)
class Packet:
    generated_on: date
    notice: str
    issues: list[IssuePacket]

    def to_dict(self) -> dict:
        return {"generated_on": self.generated_on.isoformat(), "notice": self.notice,
                "issues": [i.to_dict() for i in self.issues]}


def build_packet(entries: Iterable[EntryView], today: date, window_days: int = 90,
                 issue_id: str | None = None) -> Packet:
    """Everything the rules know about each issue, open ones first. Pure Python."""
    entries = list(entries)
    summaries = summarize_issues(entries, today)
    recurrences = detect_recurrence(summaries, today, window_days)
    conflicts = detect_conflicts(entries)
    chosen = [s for s in summaries if issue_id is None or s.issue_id == issue_id]
    chosen.sort(key=lambda s: (s.status != "open", urgency_key(s)))
    return Packet(today, NOTICE, [
        IssuePacket(
            summary=s,
            timeline=build_timeline(entries, s.issue_id),
            completeness=score_completeness(s),
            next_step=next_step(s),
            recurrence=next((r for r in recurrences if s.issue_id in r.issue_ids), None),
            conflicts=tuple(c for c in conflicts if c.issue_id == s.issue_id),
        )
        for s in chosen
    ])
