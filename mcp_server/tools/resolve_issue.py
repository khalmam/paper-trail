from mcp.server.fastmcp import FastMCP

from ledger.services import resolve_issue as resolve_service
from mcp_server.identity import resolve_identity
from mcp_server.runner import run_db

from ._common import entry_response


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def resolve_issue(room: str | None = None, note: str = "") -> dict:
        """Mark a problem as fixed. Use it only when the user says it has been repaired or is
        no longer happening, never on your own. room says which problem, like bedroom; leave it
        empty for the most recent open one. note is anything the user says about the fix.
        The record is kept, so the history can still be shown. Not legal advice."""
        who = await resolve_identity()
        entry = await run_db(
            resolve_service, household=who.household, author=who.author, note=note, room=room,
        )
        where = entry.payload.get("room") or "latest"
        return entry_response(entry, f"Marked your {where} issue as fixed, entry {entry.seq}. The history is still saved.")
