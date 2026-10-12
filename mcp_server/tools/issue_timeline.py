from mcp.server.fastmcp import FastMCP

from ledger.services import issue_timeline as timeline_service
from mcp_server.identity import resolve_identity
from mcp_server.runner import run_db


def _spoken_date(d) -> str:
    return f"{d:%B} {d.day}"


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def issue_timeline(room: str | None = None) -> dict:
        """Read back the full history of one problem in date order: when it was logged, every
        update, each time the landlord was told, deadlines, and any corrections. Use it when
        the user asks what happened, wants the history, or needs to show when something was
        reported. room says which problem, like bedroom; leave it empty for the most recent
        one. Not legal advice."""
        who = await resolve_identity()
        tl = await run_db(timeline_service, who.household, room)
        n, last = len(tl.items), tl.items[-1]
        speech = (f"Your {tl.room} {tl.category} has {n} {'entry' if n == 1 else 'entries'} on record. "
                  f"The latest, recorded {_spoken_date(last.at)}, is: {last.text}")
        return {**tl.to_dict(), "speech": speech}
