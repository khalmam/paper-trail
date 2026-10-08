from mcp.server.fastmcp import FastMCP

from ledger.services import set_deadline as set_deadline_service
from mcp_server.identity import resolve_identity
from mcp_server.runner import run_db

from ._common import entry_response


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def set_deadline(deadline: str, what: str, room: str | None = None) -> dict:
        """Record the date the landlord promised, or the user wants, a problem to be fixed by.
        deadline must be an ISO date like 2026-10-20 and must come from the user. If they did
        not give a date, ask them; never guess one and never state a legal deadline.
        what is the promised action, like fix the ceiling. room says which problem; leave it
        empty for the most recent one. Not legal advice."""
        who = await resolve_identity()
        entry = await run_db(
            set_deadline_service, household=who.household, author=who.author,
            deadline=deadline, what=what, room=room,
        )
        return entry_response(entry, f"Deadline saved for {entry.payload['deadline_date']}, entry {entry.seq}.")
