from collections.abc import Iterable
from datetime import date

from . import kinds
from .types import EntryView, IssueSummary


def _as_date(value, fallback: date) -> date:
    try:
        return date.fromisoformat(value) if value else fallback
    except ValueError:
        return fallback


def summarize_issues(entries: Iterable[EntryView], today: date) -> list[IssueSummary]:
    """One summary per logged issue, in the order the issues were logged."""
    groups: dict[str, list[EntryView]] = {}
    for e in sorted(entries, key=lambda e: e.seq):
        groups.setdefault(e.issue_id, []).append(e)
    summaries = []
    for group in groups.values():
        opener = next((e for e in group if e.kind == kinds.ISSUE_LOGGED), None)
        if opener is not None:  # entries with no opening issue are ignored
            summaries.append(_summarize(opener, group, today))
    return summaries


def _summarize(opener: EntryView, group: list[EntryView], today: date) -> IssueSummary:
    resolved = any(e.kind == kinds.RESOLVED for e in group)
    contacts = [e for e in group if e.kind == kinds.LANDLORD_CONTACT]
    last_contact = max(
        contacts, key=lambda e: _as_date(e.payload.get("contacted_on"), e.created_at.date()), default=None,
    )
    deadlines = [e for e in group if e.kind == kinds.DEADLINE_SET]
    deadline = deadlines[-1] if deadlines else None  # the most recent one the user set
    deadline_on = _as_date(deadline.payload.get("deadline_date"), today) if deadline else None
    days_left = (deadline_on - today).days if deadline_on else None
    return IssueSummary(
        issue_id=opener.issue_id,
        room=opener.payload.get("room", ""),
        category=opener.payload.get("category", ""),
        description=opener.payload.get("description", ""),
        logged_on=_as_date(opener.payload.get("happened_on"), opener.created_at.date()),
        status="resolved" if resolved else "open",
        updates=sum(1 for e in group if e.kind == kinds.UPDATE),
        contacts=len(contacts),
        last_contact_on=_as_date(last_contact.payload.get("contacted_on"), last_contact.created_at.date())
        if last_contact else None,
        last_contact_method=last_contact.payload.get("method") if last_contact else None,
        deadline_on=deadline_on,
        deadline_what=deadline.payload.get("what") if deadline else None,
        days_until_deadline=days_left,
        overdue=(not resolved) and days_left is not None and days_left < 0,
        photo_refs=sum(1 for e in group if e.payload.get("photo_ref")),
        witnesses=sum(1 for e in group if e.payload.get("witness")),
        letters_sent=sum(1 for e in group if e.kind == kinds.LETTER_SENT),
    )


def urgency_key(s: IssueSummary):
    """Sort key: overdue first (most overdue first), then nearest deadline, then no deadline (oldest first)."""
    d = s.days_until_deadline
    rank = 0 if s.overdue else (1 if d is not None else 2)
    return (rank, d if d is not None else 0, s.logged_on)
