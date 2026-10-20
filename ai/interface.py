from dataclasses import dataclass
from datetime import date
from typing import Protocol


@dataclass(frozen=True)
class ParsedIssue:
    room: str | None
    category: str | None
    description: str
    happened_on: str | None = None   # ISO date, or None meaning "today"
    question: str | None = None      # set when something essential is missing
    contact_method: str | None = None   # how the landlord was told, if the tenant said so
    contact_note: str | None = None
    contacted_on: str | None = None     # ISO date; None means today
    deadline_on: str | None = None      # only a date the tenant actually stated
    deadline_what: str | None = None

    @property
    def complete(self) -> bool:
        return self.question is None


class IssueParser(Protocol):
    def parse_issue(self, utterance: str, today: date) -> ParsedIssue:
        """Turn what the user said into fields. Never decides what to ask or what is valid."""
