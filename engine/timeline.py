from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from . import kinds
from .corrections import apply_corrections
from .types import EntryView


@dataclass(frozen=True)
class TimelineItem:
    seq: int
    kind: str
    author: str
    at: datetime
    text: str
    corrected: bool

    def to_dict(self) -> dict:
        return {"seq": self.seq, "kind": self.kind, "author": self.author,
                "at": self.at.isoformat(), "text": self.text, "corrected": self.corrected}


@dataclass(frozen=True)
class Timeline:
    issue_id: str
    room: str
    category: str
    items: list[TimelineItem]

    def to_dict(self) -> dict:
        return {"issue_id": self.issue_id, "room": self.room, "category": self.category,
                "items": [i.to_dict() for i in self.items]}


def _describe(e: EntryView) -> str:
    p = e.payload
    if e.kind == kinds.ISSUE_LOGGED:
        when = f" (happened {p['happened_on']})" if p.get("happened_on") else ""
        return f"Logged a {p.get('category', 'problem')} in the {p.get('room', 'home')}{when}: {p.get('description', '')}"
    if e.kind == kinds.UPDATE:
        extras = [f"{label}: {p[key]}" for key, label in (("photo_ref", "photo"), ("witness", "witness")) if p.get(key)]
        return f"Update: {p.get('note', '')}" + (f" ({'; '.join(extras)})" if extras else "")
    if e.kind == kinds.LANDLORD_CONTACT:
        return f"Told the landlord by {str(p.get('method', 'unknown')).replace('_', ' ')} on {p.get('contacted_on', '?')}: {p.get('note', '')}"
    if e.kind == kinds.DEADLINE_SET:
        return f"Deadline set for {p.get('deadline_date', '?')}: {p.get('what', '')}"
    if e.kind == kinds.RESOLVED:
        return "Marked as fixed" + (f": {p['note']}" if p.get("note") else "")
    if e.kind == kinds.LETTER_SENT:
        return "Letter sent to the landlord"
    if e.kind == kinds.CORRECTION:
        reason = f" Reason: {p['reason']}" if p.get("reason") else ""
        return f"Corrected {p.get('field')} of entry {p.get('corrects_seq')}: {p.get('old_value')} became {p.get('new_value')}.{reason}"
    return e.kind


def build_timeline(entries: Iterable[EntryView], issue_id: str) -> Timeline:
    """One issue's history in order, with corrections applied and flagged."""
    patched = [e for e in apply_corrections(entries) if e.issue_id == issue_id]
    opener = next((e for e in patched if e.kind == kinds.ISSUE_LOGGED), None)
    return Timeline(
        issue_id=issue_id,
        room=opener.payload.get("room", "") if opener else "",
        category=opener.payload.get("category", "") if opener else "",
        items=[TimelineItem(e.seq, e.kind, e.author, e.created_at, _describe(e), e.corrected) for e in patched],
    )
