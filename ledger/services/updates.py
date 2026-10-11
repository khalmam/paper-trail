from ledger.models import Entry, Household

from .append import append_entry
from .lookup import find_issue


def add_update(*, household: Household, author: str, note: str, room: str | None = None,
               photo_ref: str | None = None, witness: str | None = None) -> Entry:
    """Attach a note to the most recent logged issue (in `room` if given).
    photo_ref is a pointer to a photo the user holds, never the image. witness is a name."""
    issue = find_issue(household, room)
    payload = {"note": note.strip(), "room": issue.payload.get("room")}
    if photo_ref and photo_ref.strip():
        payload["photo_ref"] = photo_ref.strip()
    if witness and witness.strip():
        payload["witness"] = witness.strip()
    return append_entry(
        household=household, author=author, kind=Entry.Kind.UPDATE,
        issue_id=issue.issue_id, payload=payload,
    )
