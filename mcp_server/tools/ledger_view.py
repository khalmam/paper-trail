from mcp.server.fastmcp import FastMCP

from ledger.services.ledger_view import ledger_view as ledger_service
from mcp_server.identity import resolve_identity
from mcp_server.runner import run_db


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def ledger_view() -> dict:
        """Show the user's evidence log entry by entry, with short hashes and whether the
        chain is intact. Read only. Use it when the user wants to see the record itself."""
        who = await resolve_identity()
        data = await run_db(ledger_service, who.household)
        return {**data, "speech": f"Your log has {len(data['entries'])} entries."}
