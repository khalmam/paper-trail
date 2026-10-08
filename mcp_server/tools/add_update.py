from mcp.server.fastmcp import FastMCP

from ledger.services import add_update as add_update_service
from mcp_server.identity import resolve_identity
from mcp_server.runner import run_db

from ._common import entry_response


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def add_update(note: str, room: str | None = None) -> dict:
        """Add a new detail to a problem that was already logged, like it got worse or the
        landlord replied. Use it when the user says more about an existing issue. room says
        which problem, like bedroom; leave it empty for the most recent one. Not legal advice."""
        who = await resolve_identity()
        entry = await run_db(
            add_update_service, household=who.household, author=who.author, note=note, room=room,
        )
        where = entry.payload.get("room") or "latest"
        return entry_response(entry, f"Added to your {where} issue as entry {entry.seq}.")
