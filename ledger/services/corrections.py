from ledger.domain.corrections import validate_correction
from ledger.exceptions import NoSuchEntry
from ledger.models import Entry, Household

from .append import append_entry


def _current_value(household: Household, target: Entry, field: str):
    latest = Entry.objects.filter(
        household=household, kind=Entry.Kind.CORRECTION,
        payload__corrects_seq=target.seq, payload__field=field,
    ).order_by("-seq").first()
    return latest.payload["new_value"] if latest else target.payload.get(field)


def correct_entry(*, household: Household, author: str, seq: int, field: str,
                  new_value: str, reason: str = "") -> Entry:
    """Record a fix as a NEW entry. The original stays exactly as it was."""
    target = Entry.objects.filter(household=household, seq=seq).first()
    if target is None:
        raise NoSuchEntry(f"There is no entry number {seq} in your log.")
    value = validate_correction(target.kind, field, new_value)
    old = _current_value(household, target, field)
    if value == old:
        raise ValueError(f"The {field.replace('_', ' ')} is already set to that.")
    return append_entry(
        household=household, author=author, kind=Entry.Kind.CORRECTION, issue_id=target.issue_id,
        payload={"corrects_seq": seq, "field": field, "old_value": old,
                 "new_value": value, "reason": reason.strip()},
    )
