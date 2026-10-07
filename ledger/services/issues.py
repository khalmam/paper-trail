from datetime import date

from ledger.domain.vocab import CATEGORIES
from ledger.models import Entry

from .append import append_entry
from .households import get_or_create_household


def log_issue(*, household_name: str, author: str, room: str, category: str,
              description: str, happened_on: str | None = None) -> Entry:
    if category not in CATEGORIES:
        raise ValueError(f"category must be one of {CATEGORIES}")
    if happened_on:
        date.fromisoformat(happened_on)  # raises ValueError on bad input
    household = get_or_create_household(household_name)
    return append_entry(
        household=household, author=author, kind=Entry.Kind.ISSUE_LOGGED,
        payload={
            "room": room.strip().lower(),
            "category": category,
            "description": description.strip(),
            "happened_on": happened_on or date.today().isoformat(),
        },
    )
