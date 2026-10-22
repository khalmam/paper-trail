from mcp.server.fastmcp import FastMCP

from ledger.services import overview
from mcp_server.identity import resolve_identity
from mcp_server.runner import run_db

NUMBER_WORDS = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
MAX_SPOKEN = 5


def _days(n: int) -> str:
    return f"{n} day" if n == 1 else f"{n} days"


def _status(item) -> str:
    d = item.days_until_deadline
    if d is None:
        return "no deadline set"
    if d < 0:
        return f"{_days(-d)} past its deadline"
    if d == 0:
        return "due today"
    return f"due in {_days(d)}"


def _repeat_sentence(top, recurrences) -> str:
    rec = next((r for r in recurrences if r.room == top.room and r.category == top.category), None)
    if rec is None:
        return ""
    times = NUMBER_WORDS.get(rec.count, str(rec.count))
    return f" This kind of problem has happened {times} times in the {rec.room} in the last {rec.window_days} days."


def _speech(result) -> str:
    items = result.open
    if not items:
        return "You have no open issues."
    n = len(items)
    shown = "; ".join(f"the {i.room} {i.category} from {i.logged_on}, {_status(i)}" for i in items[:MAX_SPOKEN])
    more = f"; and {n - MAX_SPOKEN} more" if n > MAX_SPOKEN else ""
    speech = f"You have {n} open issue{'s' if n != 1 else ''}: {shown}{more}."
    speech += _repeat_sentence(items[0], result.recurrences)
    conflicts = [c for c in result.conflicts if c.issue_id == items[0].issue_id]
    if conflicts:
        speech += " " + conflicts[0].message
    return speech + " " + result.guidance[items[0].issue_id].step.message


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
        return {
            "count": len(items),
            "issues": [i.to_dict() for i in items],
            "recurrences": [r.to_dict() for r in result.recurrences],
            "conflicts": [c.to_dict() for c in result.conflicts],
            "guidance": [result.guidance[i.issue_id].to_dict() for i in items],
            "speech": _speech(result),
        }
