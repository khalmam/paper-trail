"""What may be corrected and how new values are checked. Pure Python."""
from datetime import date
from typing import Literal

from .vocab import CATEGORIES, CONTACT_METHODS

CorrectableField = Literal[
    "room", "category", "description", "happened_on", "method", "note",
    "contacted_on", "deadline_date", "what", "photo_ref", "witness",
]

FIELDS_BY_KIND = {
    "issue_logged": ("room", "category", "description", "happened_on"),
    "update": ("note", "photo_ref", "witness"),
    "landlord_contact": ("method", "note", "contacted_on"),
    "deadline_set": ("deadline_date", "what"),
}
DATE_FIELDS = {"happened_on", "contacted_on", "deadline_date"}


def validate_correction(kind: str, field: str, value: str | None) -> str:
    """Returns the cleaned new value or raises ValueError with a message fit to be spoken."""
    allowed = FIELDS_BY_KIND.get(kind)
    if allowed is None:
        raise ValueError("That kind of entry cannot be corrected.")
    if field not in allowed:
        raise ValueError(f"For that entry you can correct: {', '.join(allowed)}.")
    text = (value or "").strip()
    if not text:
        raise ValueError("The new value cannot be empty.")
    if field in {"room", "category", "method"}:
        text = text.lower()
    if field == "category" and text not in CATEGORIES:
        raise ValueError(f"The category must be one of: {', '.join(CATEGORIES)}.")
    if field == "method" and text not in CONTACT_METHODS:
        raise ValueError(f"The method must be one of: {', '.join(CONTACT_METHODS)}.")
    if field in DATE_FIELDS:
        try:
            date.fromisoformat(text)
        except ValueError:
            raise ValueError("The date must look like 2026-10-20.") from None
    return text
