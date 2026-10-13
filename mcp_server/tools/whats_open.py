from mcp.server.fastmcp import FastMCP

from ledger.services import overview
from mcp_server.identity import resolve_identity
from mcp_server.runner import run_db

NUMBER_WORDS = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}


def _days(n: int) -> str:
    return f"{n} day" if n == 1 else f"{n} days"


def _headline(top) -> str:
    text = f"Most urgent is the {top.room} {top.category}"
    d = top.days_until_deadline
    if d is None:
        return text + ", with no deadline set."
    if d < 0:
        return text + f", which is {_days(-d)} past its deadline."
    if d == 0:
        return text + ", due today."
    return text + f", due in {_days(d)}."


def _repeat_sentence(top, recurrences) -> str:
    rec = next((r for r in recurrences if r.room == top.room and r.category == top.category), None)
    if rec is None:
        return ""
    times = NUMBER_WORDS.get(rec.count, str(rec.count))
    return f" This kind of problem has happened {times} times in the {rec.room} in the last {rec.window_days} days."


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def whats_open() -> dict:
        """List the problems in the user's home that have not been fixed yet, most urgent first,
        with how many times the landlord was contacted, any deadline, and whether the same kind
        of problem keeps coming back. Use it when the user asks what is still open, outstanding,
        or overdue. Not legal advice."""
        who = await resolve_identity()
        result = await run_db(overview, who.household)
        items = result.open
        if not items:
            speech = "You have no open issues."
        else:
            n = len(items)
            speech = f"You have {n} open issue{'s' if n != 1 else ''}. " + _headline(items[0])
            speech += _repeat_sentence(items[0], result.recurrences)
            top_conflicts = [c for c in result.conflicts if c.issue_id == items[0].issue_id]
            if top_conflicts:
                speech += " " + top_conflicts[0].message
            g = result.guidance[items[0].issue_id]
            speech += " " + g.step.message
            skip = ("landlord_contact",) if g.step.action == "contact_landlord" else ()
            hint = g.completeness.next_suggestion(skip)
            if hint:
                speech += f" To strengthen your record, add {hint}."
        return {
            "count": len(items),
            "issues": [i.to_dict() for i in items],
            "recurrences": [r.to_dict() for r in result.recurrences],
            "conflicts": [c.to_dict() for c in result.conflicts],
            "guidance": [result.guidance[i.issue_id].to_dict() for i in items],
            "speech": speech,
        }
