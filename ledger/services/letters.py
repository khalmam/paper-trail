from datetime import date

from django.conf import settings
from django.utils import timezone

from engine.letter import Letter, build_letter
from engine.types import EntryView
from ledger.domain.vocab import CONTACT_METHODS
from ledger.exceptions import NoSuchIssue
from ledger.models import Entry, Household

from .append import append_entry
from .lookup import find_open_issue
from .overview import overview


def _views(household: Household) -> list[EntryView]:
    return [
        EntryView(seq=e.seq, kind=e.kind, issue_id=str(e.issue_id), author=e.author,
                  created_at=e.created_at, payload=e.payload)
        for e in Entry.objects.filter(household=household).order_by("seq")
    ]


def _target(household: Household, room: str | None, today: date) -> Entry:
    """The issue a letter is about: the one in `room`, else the most urgent open one."""
    if room:
        return find_open_issue(household, room)
    open_ones = overview(household, today).open
    if not open_ones:
        raise NoSuchIssue("There is no open issue.")
    return Entry.objects.get(household=household, kind=Entry.Kind.ISSUE_LOGGED,
                             issue_id=open_ones[0].issue_id)


def draft_letter(household: Household, room: str | None = None, today: date | None = None) -> Letter:
    """Builds a draft from the record. Reads only: nothing is written to the ledger."""
    today = today or timezone.now().date()
    issue = _target(household, room, today)
    return build_letter(_views(household), today, str(issue.issue_id), settings.RECURRENCE_WINDOW_DAYS)


def confirm_letter_sent(*, household: Household, author: str, method: str = "letter",
                        room: str | None = None, sent_on: str | None = None) -> Entry:
    """Records that the person really sent the letter. Only this writes to the ledger."""
    if method not in CONTACT_METHODS:
        raise ValueError(f"method must be one of {CONTACT_METHODS}")
    if sent_on:
        date.fromisoformat(sent_on)  # ValueError on bad input
    issue = _target(household, room, timezone.now().date())
    return append_entry(
        household=household, author=author, kind=Entry.Kind.LETTER_SENT, issue_id=issue.issue_id,
        payload={"method": method, "room": issue.payload.get("room"),
                 "sent_on": sent_on or timezone.now().date().isoformat()},
    )
