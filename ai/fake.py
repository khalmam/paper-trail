"""Deterministic keyword parser. Offline stand-in for Bedrock in tests and demos."""
import re
from datetime import date, timedelta

from .interface import ParsedIssue

CATEGORY_PATTERNS = {
    "leak": r"\b(leak|drip|flood)\w*|water (is )?coming",
    "mold": r"\b(mou?ld|damp)\w*",
    "heating": r"\b(heater|heating|radiator|boiler|ac|air.?condition\w*)\b|no heat|not cooling",
    "pests": r"\b(ants?|mice|mouse|rats?|roach(es)?|cockroach(es)?|bed ?bugs?)\b",
    "electrical": r"\b(socket|wiring|sparks?)\b|power (outage|cut)|no power",
    "structural": r"\b(cracks?|cracked|collapse\w*|sagging)\b",
}
ROOMS = ("living room", "bedroom", "bathroom", "kitchen", "hallway", "balcony", "basement")


class FakeParser:
    def parse_issue(self, utterance: str, today: date) -> ParsedIssue:
        text = utterance.lower()
        category = next((c for c, p in CATEGORY_PATTERNS.items() if re.search(p, text)), None)
        room = next((r for r in ROOMS if r in text), None)
        happened = None
        if "yesterday" in text:
            happened = (today - timedelta(days=1)).isoformat()
        elif match := re.search(r"(\d+) days? ago", text):
            happened = (today - timedelta(days=int(match.group(1)))).isoformat()
        return ParsedIssue(room, category, utterance.strip(), happened)
