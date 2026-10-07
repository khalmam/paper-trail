from mcp.server.fastmcp import FastMCP

from ledger.domain.vocab import Category
from ledger.services import log_issue as log_issue_service
from mcp_server.identity import resolve_identity
from mcp_server.runner import run_db


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def log_issue(room: str, category: Category, description: str,
                        happened_on: str | None = None) -> dict:
        """Record a new problem in the user's home, like a leak or mold, in their permanent
        evidence log. Use it when the user reports something wrong. room is where it is,
        like bedroom or kitchen. happened_on is an ISO date; leave it empty for today.
        Not legal advice."""
        who = resolve_identity()
        entry = await run_db(
            log_issue_service, household_name=who.household_name, author=who.author,
            room=room, category=category, description=description, happened_on=happened_on,
        )
        receipt = entry.hash[:8]
        return {
            "entry_number": entry.seq,
            "issue_id": str(entry.issue_id),
            "receipt": receipt,
            "speech": f"Logged. That's entry {entry.seq} in your evidence log, receipt {' '.join(receipt[:4])}.",
        }
