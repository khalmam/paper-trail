from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from . import kinds
from .corrections import apply_corrections
from .types import EntryView


@dataclass(frozen=True)
class Conflict:
    kind: str
    issue_id: str
    authors: tuple[str, ...]
    seqs: tuple[int, ...]
    message: str   # neutral, written to be spoken; never says who is right

    def to_dict(self) -> dict:
        return {"kind": self.kind, "issue_id": self.issue_id, "authors": list(self.authors),
                "seqs": list(self.seqs), "message": self.message}


def _names(authors: Iterable[str]) -> str:
    names = sorted(set(authors))
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def _label(openers: dict[str, EntryView], issue_id: str) -> str:
    o = openers.get(issue_id)
    return f"{o.payload.get('room', 'home')} {o.payload.get('category', 'problem')}" if o else "issue"


def _date(value) -> date | None:
    try:
        return date.fromisoformat(value) if value else None
    except ValueError:
        return None


def _deadline_conflicts(issue_id: str, label: str, group: list[EntryView]) -> list[Conflict]:
    latest: dict[str, EntryView] = {}
    for e in group:  # group is in seq order, so the last one per author wins
        if e.kind == kinds.DEADLINE_SET:
            latest[e.author] = e
    if len(latest) < 2 or len({e.payload.get("deadline_date") for e in latest.values()}) < 2:
        return []
    authors = tuple(sorted(latest))
    seqs = tuple(sorted(e.seq for e in latest.values()))
    return [Conflict("deadline_differs", issue_id, authors, seqs,
                     f"{_names(authors)} recorded different deadlines for the {label}.")]


def _reopened(issue_id: str, label: str, group: list[EntryView]) -> list[Conflict]:
    fixed = next((e for e in group if e.kind == kinds.RESOLVED), None)
    if fixed is None:
        return []
    watched = (kinds.UPDATE, kinds.LANDLORD_CONTACT, kinds.DEADLINE_SET)
    later = [e for e in group if e.seq > fixed.seq and e.author != fixed.author and e.kind in watched]
    if not later:
        return []
    authors = tuple(sorted({fixed.author} | {e.author for e in later}))
    return [Conflict("reopened_after_fix", issue_id, authors, (fixed.seq, *(e.seq for e in later)),
                     f"{fixed.author} marked the {label} as fixed, but "
                     f"{_names(e.author for e in later)} added to it afterwards.")]


def _correction_disputes(raw: list[EntryView]) -> list[Conflict]:
    groups: dict[tuple, list[EntryView]] = defaultdict(list)
    for e in raw:
        if e.kind == kinds.CORRECTION and e.payload.get("field"):
            groups[(e.payload.get("corrects_seq"), e.payload["field"])].append(e)
    found = []
    for (target, field), items in groups.items():
        authors = {e.author for e in items}
        if len(authors) < 2 or len({str(e.payload.get("new_value")) for e in items}) < 2:
            continue
        found.append(Conflict(
            "correction_dispute", items[0].issue_id, tuple(sorted(authors)), tuple(e.seq for e in items),
            f"{_names(authors)} corrected the {field.replace('_', ' ')} on entry {target} to different values."))
    return found


def _similar(openers: list[EntryView], max_gap_days: int) -> list[Conflict]:
    items = sorted(openers, key=lambda e: e.seq)
    found = []
    for i, a in enumerate(items):
        for b in items[i + 1:]:
            same_kind_of_problem = (a.payload.get("room"), a.payload.get("category")) == \
                                   (b.payload.get("room"), b.payload.get("category"))
            da, db = _date(a.payload.get("happened_on")), _date(b.payload.get("happened_on"))
            if a.author == b.author or not same_kind_of_problem or da is None or db is None:
                continue
            gap = abs((da - db).days)
            if 1 <= gap <= max_gap_days:
                unit = "day" if gap == 1 else "days"
                found.append(Conflict(
                    "similar_reports", b.issue_id, tuple(sorted({a.author, b.author})), (a.seq, b.seq),
                    f"{_names([a.author, b.author])} each logged a {a.payload.get('room')} "
                    f"{a.payload.get('category')}, {gap} {unit} apart. These may be the same problem "
                    f"recorded with different dates."))
    return found


def detect_conflicts(entries: Iterable[EntryView], similar_days: int = 3) -> list[Conflict]:
    """Places where roommates' records disagree. Flags are prompts to review, never verdicts."""
    raw = sorted(entries, key=lambda e: e.seq)
    patched = apply_corrections(raw)
    openers = {e.issue_id: e for e in patched if e.kind == kinds.ISSUE_LOGGED}
    by_issue: dict[str, list[EntryView]] = defaultdict(list)
    for e in patched:
        by_issue[e.issue_id].append(e)
    found: list[Conflict] = []
    for issue_id, group in by_issue.items():
        if issue_id in openers:
            label = _label(openers, issue_id)
            found += _deadline_conflicts(issue_id, label, group)
            found += _reopened(issue_id, label, group)
    found += _correction_disputes(raw)
    found += _similar(list(openers.values()), similar_days)
    return sorted(found, key=lambda c: (min(c.seqs), c.kind))
