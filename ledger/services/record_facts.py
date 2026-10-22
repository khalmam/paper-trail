from collections import defaultdict
from datetime import date

from django.utils import timezone

from ledger.models import Entry, Household

from .overview import overview

MAX_ENTRIES = 80


def record_facts(household: Household, today: date | None = None) -> dict:
    """The record as plain facts for answering questions. Reads only."""
    today = today or timezone.now().date()
    entries = list(Entry.objects.filter(household=household).order_by("seq"))
    groups = defaultdict(list)
    for e in entries:
        groups[str(e.issue_id)].append(e)
    result = overview(household, today)
    open_issues = []
    for s in result.open:
        group = groups.get(str(s.issue_id), [])
        open_issues.append({
            "room": s.room, "category": s.category, "description": s.description,
            "first_reported": str(s.logged_on), "days_until_deadline": s.days_until_deadline,
            "landlord_contacts": [
                {"method": e.payload.get("method"), "note": e.payload.get("note"), "by": e.author,
                 "on": e.payload.get("contacted_on") or e.created_at.date().isoformat()}
                for e in group if e.kind == Entry.Kind.LANDLORD_CONTACT],
            "deadlines_recorded": [
                {"date": e.payload.get("deadline_date"), "what": e.payload.get("what"), "set_by": e.author}
                for e in group if e.kind == Entry.Kind.DEADLINE_SET],
            "letters_sent_on": [e.payload.get("sent_on") for e in group if e.kind == Entry.Kind.LETTER_SENT],
        })
        o = open_issues[-1]
        o["landlord_contact_count"] = len(o["landlord_contacts"])
        o["deadline_count"] = len(o["deadlines_recorded"])
        o["letters_sent_count"] = len(o["letters_sent_on"])
        o["label"] = f"{s.room} {s.category} first reported {s.logged_on}"
    return {
        "today": today.isoformat(),
        "open_issues": open_issues,
        "recurrences": [r.to_dict() for r in result.recurrences],
        "conflicts": [c.to_dict() for c in result.conflicts],
        "entries": [{"seq": e.seq, "kind": e.kind, "author": e.author,
                     "date": e.created_at.date().isoformat(), "details": e.payload}
                    for e in entries[-MAX_ENTRIES:]],
    }
