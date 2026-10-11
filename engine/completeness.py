from dataclasses import dataclass

from .types import IssueSummary

SUGGESTIONS = {
    "date": "the date it happened",
    "location": "which room it is in",
    "photo": "a note saying where a photo is saved",
    "witness": "the name of someone who saw it",
    "landlord_contact": "a record of telling your landlord",
}


@dataclass(frozen=True)
class Completeness:
    percent: int
    present: tuple[str, ...]
    missing: tuple[str, ...]

    def to_dict(self) -> dict:
        return {"percent": self.percent, "present": list(self.present), "missing": list(self.missing)}

    def next_suggestion(self, skip: tuple[str, ...] = ()) -> str | None:
        for item in self.missing:
            if item not in skip:
                return SUGGESTIONS[item]
        return None


def score_completeness(s: IssueSummary) -> Completeness:
    checks = {
        "date": s.logged_on is not None,
        "location": bool(s.room),
        "photo": s.photo_refs > 0,
        "witness": s.witnesses > 0,
        "landlord_contact": s.contacts > 0,
    }
    present = tuple(k for k, ok in checks.items() if ok)
    missing = tuple(k for k, ok in checks.items() if not ok)
    return Completeness(round(100 * len(present) / len(checks)), present, missing)
