"""Decides what a chat message means. Pure Python: rules route, the parser only reads problem reports."""
import re
from dataclasses import dataclass, replace
from datetime import date

from ai.guards import BudgetExceeded, CallBudget, call_with_retries
from ai.interface import IssueParser
from ai.validate import CATEGORIES, enforce_vocab, parse_checked

MAX_CHARS = 500  # caps what one message can cost

VERIFY = re.compile(r"\b(intact|tamper\w*|altered|verify|integrity)\b", re.I)
PACKET = re.compile(r"\b(packet|full record)\b", re.I)
DRAFT = re.compile(r"\b(draft|write|prepare|make)\s+(me\s+)?(a|the|my)?\s*(formal\s+)?letter\b|\bletter\s+to\s+(my|the)\s+(landlord|property manager)\b", re.I)
SENT = re.compile(r"\b(i|we)\s+(already\s+|just\s+)?(sent|mailed|posted|delivered)\s+(the|my|our|that)\s+letter\b|\b(the|my|our)\s+letter\s+(was|has been|got)\s+(sent|mailed|posted|delivered)\b", re.I)
OPEN = re.compile(r"\bwhat('?s| is| are)?\b.*\b(open|outstanding)\b|\bopen (issues|problems)\b", re.I)


QUESTION = re.compile(r"\?\s*$|^\s*(when|which|who|whom|whose|what|why|how|did|do|does|have|has|is|are|was|were|am|any|list|show|tell|explain|summari[sz]e)\b", re.I)
ASKS_TO_ACT = re.compile(r"^\s*(please\b|(can|could|would|will)\s+you\b)", re.I)


@dataclass(frozen=True)
class Action:
    """tool set: the endpoint calls it and speaks its answer. tool None: speak `reply`."""
    tool: str | None
    arguments: dict
    reply: str | None = None
    pending: dict | None = None  # sent back by the client with the next message
    then: tuple = ()  # further (tool, arguments) calls, made in order after the first
    ask: str | None = None  # a question about the record: answered from facts, never written


def route(message: str, today: date, parser: IssueParser, budget: CallBudget,
          pending: dict | None = None) -> Action:
    text = (message or "").strip()[:MAX_CHARS]
    if not text:
        return Action(None, {}, "Tell me what's going on, like a leak in the bedroom.", pending)
    if VERIFY.search(text):
        return Action("verify_integrity", {})
    if DRAFT.search(text):
        return Action("draft_letter", {})
    if SENT.search(text):
        return Action("confirm_letter_sent", {})
    if PACKET.search(text):
        return Action("evidence_packet", {})
    if OPEN.search(text):
        return Action("whats_open", {})
    if not pending and QUESTION.search(text) and not ASKS_TO_ACT.search(text):
        return Action("record_facts", {}, ask=text)

    utterance = f"{pending.get('utterance', '')} {text}".strip() if pending else text
    try:
        parsed = call_with_retries(lambda: parse_checked(parser, utterance, today), budget)
    except BudgetExceeded as exc:
        return Action(None, {}, f"{exc} Everything else still works.")
    except Exception:
        return Action(None, {}, "I couldn't work that out. Could you say it another way?", pending)
    parsed = _apply_answer(parsed, pending, text, today)
    if not parsed.complete:
        asked = "room" if parsed.room is None else "category"
        return Action(None, {}, parsed.question, {"utterance": utterance, "asked": asked})

    if parsed.category == "other" and len((parsed.description or "").split()) < 3:
        return Action(None, {}, f"What is the problem in the {parsed.room}?",
                      {"utterance": utterance, "asked": "description"})
    args = {"room": parsed.room, "category": parsed.category,
            "description": parsed.description or utterance}
    if parsed.happened_on:
        args["happened_on"] = parsed.happened_on
    follow = []
    if parsed.contact_method:
        contact = {"method": parsed.contact_method, "room": parsed.room,
                   "note": parsed.contact_note or "Told the landlord about the problem"}
        if parsed.contacted_on:
            contact["contacted_on"] = parsed.contacted_on
        follow.append(("record_landlord_contact", contact))
    if parsed.deadline_on:
        follow.append(("set_deadline", {"deadline": parsed.deadline_on, "room": parsed.room,
                                        "what": parsed.deadline_what or "fix the problem"}))
    return Action("log_issue", args, then=tuple(follow))


LEAD_IN = re.compile(r"^(it'?s |it is |in |the |my )+")


def _apply_answer(parsed, pending, text, today):
    """The user just answered our question. Take a short reply as the answer even if the parser can't read it."""
    asked = (pending or {}).get("asked")
    if asked == "room" and parsed.room is None and len(text) <= 40:
        room = LEAD_IN.sub("", text.lower().strip(" .!?")) or None
        return enforce_vocab(replace(parsed, room=room), today)
    if asked == "category" and parsed.category is None:
        word = next((c for c in CATEGORIES if c in text.lower()), None)
        if word:
            return enforce_vocab(replace(parsed, category=word), today)
    return parsed
