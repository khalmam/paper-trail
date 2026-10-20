"""A draft letter built only from facts in the record. Pure Python; it writes nothing."""
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from .recurrence import detect_recurrence
from .summary import summarize_issues
from .types import EntryView

NOTE = ("This is a draft for you to review. Check every fact, fill in the three bracketed parts, "
        "and send it yourself. It is not legal advice.")
PLACEHOLDERS = ("[Landlord or property manager]", "[date you choose]", "[Your name]")


@dataclass(frozen=True)
class Letter:
    subject: str
    body: str
    note: str
    placeholders: tuple[str, ...]
    issue_id: str

    def to_dict(self) -> dict:
        return {"subject": self.subject, "body": self.body, "note": self.note,
                "placeholders": list(self.placeholders), "issue_id": self.issue_id}


def _days(n: int) -> str:
    return f"{n} day{'s' if n != 1 else ''}"


def build_letter(entries: Iterable[EntryView], today: date, issue_id: str,
                 window_days: int = 90) -> Letter:
    entries = list(entries)
    summaries = summarize_issues(entries, today)
    s = next((x for x in summaries if x.issue_id == issue_id), None)
    if s is None:
        raise ValueError("There is no such problem in the record.")
    if s.status != "open":
        raise ValueError("That problem is already marked as fixed.")
    rec = next((r for r in detect_recurrence(summaries, today, window_days) if issue_id in r.issue_ids), None)

    lines = [f"Dear {PLACEHOLDERS[0]},", "",
             f"I am writing about the {s.category} in the {s.room}, which I first reported on "
             f"{s.logged_on}: {s.description}."]
    if rec:
        lines.append(f"This kind of problem has been recorded {rec.count} times in the {s.room} between "
                     f"{rec.first_on} and {rec.latest_on}.")
    if s.contacts:
        method = str(s.last_contact_method).replace("_", " ")
        lines.append(f"I told you about it by {method} on {s.last_contact_on}.")
    else:
        lines.append("I am writing to make sure you are aware of it.")
    if s.deadline_on:
        what = f" ({s.deadline_what})" if s.deadline_what else ""
        late = -s.days_until_deadline if s.days_until_deadline is not None and s.days_until_deadline < 0 else 0
        if late:
            lines.append(f"The date set for this to be fixed{what} was {s.deadline_on}. That date passed "
                         f"{_days(late)} ago, and my record does not show that the problem has been fixed.")
        else:
            lines.append(f"The date set for this to be fixed{what} is {s.deadline_on}.")
    lines += ["", f"Please let me know in writing by {PLACEHOLDERS[1]} when the repair will be done. "
              "I have kept a dated record of this problem.", "", "Yours sincerely,", PLACEHOLDERS[2]]
    return Letter(
        subject=f"Update needed on the {s.room} {s.category} reported on {s.logged_on}",
        body="\n".join(lines), note=NOTE, placeholders=PLACEHOLDERS, issue_id=issue_id)
