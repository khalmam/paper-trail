from ledger.models import Household, Entry

from .verify import verify_chain


def _summary(e: Entry) -> str:
    p = e.payload or {}
    text = p.get("description") or p.get("note") or p.get("what") or p.get("method") or ""
    return f"{p.get('room', '')} {text}".strip()[:90]


def ledger_view(household: Household) -> dict:
    """Read-only view of the chain plus the integrity result. Writes nothing."""
    entries = list(Entry.objects.filter(household=household).order_by("seq"))
    r = verify_chain(household)
    return {
        "entries": [{"seq": e.seq, "kind": e.kind, "author": e.author,
                     "date": e.created_at.date().isoformat(), "hash": e.hash[:8],
                     "prev_hash": e.prev_hash[:8], "summary": _summary(e)} for e in entries],
        "integrity": {"ok": r.ok, "verified": r.verified, "bad_seq": r.bad_seq, "reason": r.reason},
    }
