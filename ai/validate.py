from datetime import date

from ledger.domain.vocab import CATEGORIES

from .interface import IssueParser, ParsedIssue

QUESTIONS = {
    "room": "Which room is it in?",
    "category": "What kind of problem is it: a leak, mold, heating, pests, something structural, or electrical?",
}


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
    return ParsedIssue(room, category, (raw.description or "").strip(), happened, question)


def parse_checked(parser: IssueParser, utterance: str, today: date) -> ParsedIssue:
    return enforce_vocab(parser.parse_issue(utterance, today), today)
