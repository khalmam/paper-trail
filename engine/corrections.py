from collections.abc import Iterable
from dataclasses import replace

from . import kinds
from .types import EntryView


def apply_corrections(entries: Iterable[EntryView]) -> list[EntryView]:
    """Entries in seq order with corrections applied; later corrections win. The ledger is
    never edited, this only changes how the engine reads it."""
    ordered = sorted(entries, key=lambda e: e.seq)
    by_seq = {e.seq: e for e in ordered}
    patched: dict[int, dict] = {}
    for e in ordered:
        if e.kind != kinds.CORRECTION:
            continue
        target = by_seq.get(e.payload.get("corrects_seq"))
        field = e.payload.get("field")
        if target is None or not field or target.kind == kinds.CORRECTION or target.seq >= e.seq:
            continue
        patched.setdefault(target.seq, dict(target.payload))[field] = e.payload.get("new_value")
    return [replace(e, payload=patched[e.seq], corrected=True) if e.seq in patched else e for e in ordered]
