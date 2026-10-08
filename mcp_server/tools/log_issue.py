from mcp.server.fastmcp import FastMCP

from ledger.domain.vocab import Category
from ledger.services import log_issue as log_issue_service
from mcp_server.identity import resolve_identity
from mcp_server.runner import run_db

from ._common import entry_response


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def log_issue(room: str, category: Category, description: str,
                        happened_on: str | None = None) -> dict:
        """Record a new problem in the user's home, like a leak or mold, in their permanent
        evidence log. Use it when the user reports something wrong. room is where it is,
        like bedroom or kitchen. happened_on is an ISO date; leave it empty for today.
        Not legal advice."""
        who = await resolve_identity()
        entry = await run_db(
            log_issue_service, household=who.household, author=who.author,
            room=room, category=category, description=description, happened_on=happened_on,
        )
        return entry_response(entry, f"Logged. That's entry {entry.seq} in your evidence log.")
