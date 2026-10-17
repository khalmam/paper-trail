"""Decides what a chat message means. Pure Python: rules route, the parser only reads problem reports."""
import re
from dataclasses import dataclass
from datetime import date

from ai.guards import BudgetExceeded, CallBudget, call_with_retries
from ai.interface import IssueParser
from ai.validate import parse_checked

MAX_CHARS = 500  # caps what one message can cost

VERIFY = re.compile(r"\b(intact|tamper\w*|altered|verify|integrity)\b", re.I)
PACKET = re.compile(r"\b(packet|full record)\b", re.I)
OPEN = re.compile(r"\bwhat('?s| is| are)?\b.*\b(open|outstanding)\b|\bopen (issues|problems)\b", re.I)


@dataclass(frozen=True)
class Action:
    """tool set: the endpoint calls it and speaks its answer. tool None: speak `reply`."""
    tool: str | None
    arguments: dict
    reply: str | None = None
    pending: dict | None = None  # sent back by the client with the next message


def route(message: str, today: date, parser: IssueParser, budget: CallBudget,
          pending: dict | None = None) -> Action:
    text = (message or "").strip()[:MAX_CHARS]
    if not text:
        return Action(None, {}, "Tell me what's going on, like a leak in the bedroom.", pending)
    if VERIFY.search(text):
        return Action("verify_integrity", {})
    if PACKET.search(text):
        return Action("evidence_packet", {})
    if OPEN.search(text):
        return Action("whats_open", {})

    utterance = f"{pending.get('utterance', '')} {text}".strip() if pending else text
    try:
        parsed = call_with_retries(lambda: parse_checked(parser, utterance, today), budget)
    except BudgetExceeded as exc:
        return Action(None, {}, f"{exc} Everything else still works.")
    except Exception:
        return Action(None, {}, "I couldn't work that out. Could you say it another way?", pending)
    if not parsed.complete:
        return Action(None, {}, parsed.question, {"utterance": utterance})

    args = {"room": parsed.room, "category": parsed.category,
            "description": parsed.description or text}
    if parsed.happened_on:
        args["happened_on"] = parsed.happened_on
    return Action("log_issue", args)
