from datetime import date

from ledger.domain.vocab import CATEGORIES
from ledger.models import Entry, Household

from .append import append_entry


_PLACEHOLDERS = {"unknown", "none", "n/a", "na", "null", "undefined", "other", "tbd", "?"}


def _clean(label: str, value: str) -> str:
    """Refuse empty or placeholder text, so a guess never becomes a permanent entry."""
    v = (value or "").strip()
    if not v or "<" in v or ">" in v or v.lower().strip("[]() ") in _PLACEHOLDERS:
        raise ValueError(f"The {label} is missing. Ask the person for it instead of guessing.")
    return v


def log_issue(*, household: Household, author: str, room: str, category: str,
              description: str, happened_on: str | None = None) -> Entry:
    room = _clean("room", room)
    description = _clean("description", description)
    if category not in CATEGORIES:
        raise ValueError(f"category must be one of {CATEGORIES}")
    if happened_on:
        date.fromisoformat(happened_on)  # raises ValueError on bad input
    return append_entry(
        household=household, author=author, kind=Entry.Kind.ISSUE_LOGGED,
        payload={
            "room": room.strip().lower(),
            "category": category,
            "description": description.strip(),
            "happened_on": happened_on or date.today().isoformat(),
        },
    )
