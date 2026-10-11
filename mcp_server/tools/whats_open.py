from mcp.server.fastmcp import FastMCP

from ledger.services import open_issues
from mcp_server.identity import resolve_identity
from mcp_server.runner import run_db


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


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def whats_open() -> dict:
        """List the problems in the user's home that have not been fixed yet, most urgent first,
        with how many times the landlord was contacted and any deadline. Use it when the user
        asks what is still open, outstanding, or overdue. Not legal advice."""
        who = await resolve_identity()
        items = await run_db(open_issues, who.household)
        if not items:
            speech = "You have no open issues."
        else:
            n = len(items)
            speech = f"You have {n} open issue{'s' if n != 1 else ''}. " + _headline(items[0])
        return {"count": len(items), "issues": [i.to_dict() for i in items], "speech": speech}
