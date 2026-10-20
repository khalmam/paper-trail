import re
from dataclasses import replace
from datetime import date, timedelta

from ledger.domain.vocab import CATEGORIES, CONTACT_METHODS

from .interface import IssueParser, ParsedIssue

QUESTIONS = {
    "room": "Which room is it in?",
    "category": "What kind of problem is it: a leak, mold, heating, pests, something structural, or electrical?",
}


def _iso(value, today, allow_future):
    if not value:
        return None
    try:
        day = date.fromisoformat(value)
    except ValueError:
        return None
    return None if (day > today and not allow_future) else value


def enforce_vocab(raw: ParsedIssue, today: date) -> ParsedIssue:
    """Force any parser's output into our fixed lists. Rules, not the model, choose the question."""
    room = (raw.room or "").strip().lower() or None
    category = (raw.category or "").strip().lower()
    category = category if category in CATEGORIES else None
    happened = raw.happened_on
    if happened:
        try:
            if date.fromisoformat(happened) > today:
                happened = None
        except ValueError:
            happened = None
    question = QUESTIONS["room"] if room is None else (QUESTIONS["category"] if category is None else None)
    method = raw.contact_method if raw.contact_method in CONTACT_METHODS else None
    return ParsedIssue(
        room, category, (raw.description or "").strip(), happened, question,
        contact_method=method,
        contact_note=((raw.contact_note or "").strip() or None) if method else None,
        contacted_on=_iso(raw.contacted_on, today, False) if method else None,
        deadline_on=_iso(raw.deadline_on, today, True),
        deadline_what=(raw.deadline_what or "").strip() or None,
    )


WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


def weekday_date(utterance: str, today: date) -> str | None:
    """If the sentence names a weekday, the next one (never today) is computed here, not by the model."""
    found = [d for d in WEEKDAYS if re.search(rf"\b{d}\b", utterance.lower())]
    if len(found) != 1:
        return None
    ahead = (WEEKDAYS.index(found[0]) - today.weekday()) % 7 or 7
    return (today + timedelta(days=ahead)).isoformat()


def parse_checked(parser: IssueParser, utterance: str, today: date) -> ParsedIssue:
    raw = parser.parse_issue(utterance, today)
    named = weekday_date(utterance, today)
    if named and raw.deadline_on:
        raw = replace(raw, deadline_on=named)  # code, not the model, does the date arithmetic
    return enforce_vocab(raw, today)
