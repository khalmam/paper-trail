from dataclasses import asdict, dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class EntryView:
    """The engine's own plain-data view of a ledger entry."""
    seq: int
    kind: str
    issue_id: str
    author: str
    created_at: datetime
    payload: dict


@dataclass(frozen=True)
class IssueSummary:
    issue_id: str
    room: str
    category: str
    description: str
    logged_on: date
    status: str                      # "open" or "resolved"
    updates: int
    contacts: int
    last_contact_on: date | None
    last_contact_method: str | None
    deadline_on: date | None
    deadline_what: str | None
    days_until_deadline: int | None  # negative means overdue
    overdue: bool
    photo_refs: int = 0
    witnesses: int = 0
    letters_sent: int = 0

    def to_dict(self) -> dict:
        return {k: (v.isoformat() if isinstance(v, date) else v) for k, v in asdict(self).items()}
