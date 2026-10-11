from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta

from .types import IssueSummary


@dataclass(frozen=True)
class Recurrence:
    room: str
    category: str
    count: int
    window_days: int
    first_on: date
    latest_on: date
    issue_ids: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "room": self.room, "category": self.category, "count": self.count,
            "window_days": self.window_days, "first_on": self.first_on.isoformat(),
            "latest_on": self.latest_on.isoformat(), "issue_ids": list(self.issue_ids),
        }


def detect_recurrence(summaries: Iterable[IssueSummary], today: date,
                      window_days: int = 90, min_count: int = 2) -> list[Recurrence]:
    """Same room and category logged `min_count`+ times in the last `window_days` days
    (today included). Open and resolved issues both count."""
    start = today - timedelta(days=window_days)
    groups: dict[tuple[str, str], list[IssueSummary]] = defaultdict(list)
    for s in summaries:
        if start < s.logged_on <= today:
            groups[(s.room, s.category)].append(s)
    found = []
    for (room, category), items in groups.items():
        if len(items) >= min_count:
            items.sort(key=lambda s: s.logged_on)
            found.append(Recurrence(
                room, category, len(items), window_days,
                items[0].logged_on, items[-1].logged_on, tuple(s.issue_id for s in items),
            ))
    return sorted(found, key=lambda r: (-r.count, -r.latest_on.toordinal()))
