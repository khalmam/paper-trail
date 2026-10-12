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

    @property
    def complete(self) -> bool:
        return self.question is None


class IssueParser(Protocol):
    def parse_issue(self, utterance: str, today: date) -> ParsedIssue:
        """Turn what the user said into fields. Never decides what to ask or what is valid."""
