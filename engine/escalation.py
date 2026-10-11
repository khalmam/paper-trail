from dataclasses import dataclass

from .types import IssueSummary


@dataclass(frozen=True)
class Step:
    action: str    # none | contact_landlord | set_deadline | wait | reminder | letter | packet
    message: str   # written to be spoken

    def to_dict(self) -> dict:
        return {"action": self.action, "message": self.message}


def _days(n: int) -> str:
    return f"{n} day" if n == 1 else f"{n} days"


def next_step(s: IssueSummary, letter_after_days: int = 7) -> Step:
    """Suggest the next step from the user's own facts. These thresholds are product
    defaults, not legal rules, and the wording says so."""
    if s.status == "resolved":
        return Step("none", "This one is marked as fixed.")
    if s.contacts == 0:
        return Step("contact_landlord", "There is no record yet of telling your landlord. "
                    "Tell them, and then let me know so I can log it.")
    if s.deadline_on is None:
        return Step("set_deadline", "Ask your landlord for a date to fix it, "
                    "then tell me the date so I can keep track.")
    if not s.overdue:
        left = s.days_until_deadline
        if left == 0:
            return Step("wait", "The deadline you set is today.")
        return Step("wait", f"The deadline you set is in {_days(left)}. Nothing to do yet.")
    late = -s.days_until_deadline
    if s.letters_sent > 0:
        return Step("packet", f"It is {_days(late)} past your deadline and a letter was already sent. "
                    "The next step is putting together an evidence packet.")
    if late >= letter_after_days:
        return Step("letter", f"It is {_days(late)} past your deadline. "
                    "I can draft a formal letter for you to review and send yourself.")
    return Step("reminder", f"Your deadline passed {_days(late)} ago. "
                "A friendly reminder to your landlord is a good next step.")
