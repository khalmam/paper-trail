"""Decides what a chat message means. Pure Python: rules route, the parser only reads problem reports."""
import re
from dataclasses import dataclass, replace
from datetime import date

from ai.guards import BudgetExceeded, CallBudget, call_with_retries
from django.core import signing

from ai.interface import IssueParser, ParsedIssue
from ai.validate import CATEGORIES, enforce_vocab, parse_checked

MAX_CHARS = 500  # caps what one message can cost

VERIFY = re.compile(r"\b(intact|tamper\w*|altered|verify|integrity)\b", re.I)
PACKET = re.compile(r"\b(packet|full record)\b", re.I)
DRAFT = re.compile(r"\b(draft|write|prepare|make)\s+(me\s+)?(a|the|my)?\s*(formal\s+)?letter\b|\bletter\s+to\s+(my|the)\s+(landlord|property manager)\b", re.I)
SENT = re.compile(r"\b(i|we)\s+(already\s+|just\s+)?(sent|mailed|posted|delivered)\s+(the|my|our|that)\s+letter\b|\b(the|my|our)\s+letter\s+(was|has been|got)\s+(sent|mailed|posted|delivered)\b", re.I)
OPEN = re.compile(r"\bwhat('?s| is| are)?\b.*\b(open|outstanding)\b|\bopen (issues|problems)\b", re.I)


QUESTION = re.compile(r"\?\s*$|^\s*(when|which|who|whom|whose|what|why|how|did|do|does|have|has|is|are|was|were|am|any|list|show|tell|explain|summari[sz]e)\b", re.I)
GREETING = re.compile(r"^\s*(hi|hello|hey|yo|thanks|thank you|good (morning|afternoon|evening))\b[\s!.,]*$", re.I)
CANCEL = re.compile(r"^\s*(cancel|never ?mind|forget it|start over)\b[\s!.]*$", re.I)
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
          pending: dict | None = None, converser=None, history=None) -> Action:
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
    if pending and pending.get("confirm"):
        step = _confirm_step(text, pending)
        if step is not None:
            return step
        pending = None
    if converser is not None:
        smart = _smart(text, today, converser, budget, history)
        if smart is not None:
            return smart
    if CANCEL.search(text):
        return Action(None, {}, "Okay, I dropped that. Tell me what is wrong, or ask what is open.")
    if GREETING.match(text):
        return Action(None, {}, "Hi. Tell me what is wrong, like a leak in the bedroom, or ask what is open.")
    if not pending:
        asking = QUESTION.search(text)
    elif pending.get("asked") == "description":
        asking = text.rstrip().endswith("?")
    else:
        asking = text.rstrip().endswith("?") and len(text.split()) > 4
    if asking and not ASKS_TO_ACT.search(text):
        return Action("record_facts", {}, ask=text)
    if pending and pending.get("asked") == "description" and pending.get("room"):
        text = f"{text} in the {pending['room']}"
        pending = None

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
                      {"utterance": utterance, "asked": "description", "room": parsed.room})
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


YES = re.compile(r"^\s*(yes|yep|yeah|yup|correct|right|that'?s right|confirm|ok|okay|sure|do it|go ahead)\b[\s!.,]*$", re.I)
NO = re.compile(r"^\s*(no|nope|nah|wrong|not quite)\b[\s!.,]*$", re.I)
WRITES = {"log_issue", "record_landlord_contact", "set_deadline"}
SALT = "paper-trail-confirm"


def _confirm_step(text, pending):
    """The person is answering 'Is that right?'. Only a signed, unexpired proposal can be written."""
    if NO.match(text):
        return Action(None, {}, "Okay, I won't log it. What should I change?")
    if not YES.match(text):
        return None
    try:
        calls = signing.loads(pending["confirm"], salt=SALT, max_age=900)
        ok = bool(calls) and all(c[0] in WRITES for c in calls)
    except Exception:
        ok = False
    if not ok:
        return Action(None, {}, "That confirmation expired. Please tell me the problem again.")
    first, *rest = calls
    return Action(first[0], first[1], then=tuple((n, a) for n, a in rest))


def _smart(text, today, converser, budget, history):
    """The model decides what the message is. None means: use the rules instead."""
    try:
        d = call_with_retries(lambda: converser.decide(text, history, today), budget, max_attempts=1)
    except Exception:
        return None
    kind = d.get("action")
    if kind == "question":
        return Action("record_facts", {}, ask=text)
    if kind == "report":
        return _propose(d, today)
    reply = str(d.get("reply") or "").strip()[:300]
    return Action(None, {}, reply) if reply else None


def _propose(d, today):
    """Check the model's report, then ask for confirmation. Nothing is written here."""
    ask = str(d.get("reply") or "").strip()[:200]
    room = str(d.get("room") or "").strip().lower()
    if not room or len(room.split()) > 3 or "?" in room:
        return Action(None, {}, ask or "Which room is it in?")
    parsed = ParsedIssue(
        room=room, category=d.get("category") or None,
        description=str(d.get("description") or "").strip(),
        happened_on=d.get("happened_on") or None, contact_method=d.get("contact_method") or None,
        contact_note=d.get("contact_note") or None, contacted_on=d.get("contacted_on") or None,
        deadline_on=d.get("deadline_on") or None, deadline_what=d.get("deadline_what") or None)
    try:
        parsed = enforce_vocab(parsed, today)
    except Exception:
        return None
    if not parsed.complete:
        return Action(None, {}, parsed.question)
    if len((parsed.description or "").split()) < 3:
        return Action(None, {}, ask or f"What is the problem in the {parsed.room}?")
    args = {"room": parsed.room, "category": parsed.category, "description": parsed.description}
    if parsed.happened_on:
        args["happened_on"] = parsed.happened_on
    calls = [["log_issue", args]]
    reply = f"I'll log a {parsed.category} in the {parsed.room}: {parsed.description}."
    if parsed.contact_method:
        contact = {"method": parsed.contact_method, "room": parsed.room,
                   "note": parsed.contact_note or "Told the landlord about the problem"}
        if parsed.contacted_on:
            contact["contacted_on"] = parsed.contacted_on
        calls.append(["record_landlord_contact", contact])
        reply += f" I'll also note that you told the landlord by {parsed.contact_method}."
    if parsed.deadline_on:
        calls.append(["set_deadline", {"deadline": parsed.deadline_on, "room": parsed.room,
                                       "what": parsed.deadline_what or "fix the problem"}])
        reply += f" And a deadline of {parsed.deadline_on}."
    return Action(None, {}, reply + " Is that right?", {"confirm": signing.dumps(calls, salt=SALT)})
