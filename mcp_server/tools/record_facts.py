from mcp.server.fastmcp import FastMCP

from ledger.services.record_facts import record_facts as facts_service
from mcp_server.identity import resolve_identity
from mcp_server.runner import run_db


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def record_facts() -> dict:
        """Everything in the user's record as plain facts: open problems with their dates,
        landlord contacts and deadlines, repeats, disagreements between roommates, and the
        entries themselves. Read only. Use it to answer any question about the record, like
        when the landlord was first told or which problem has the most contacts."""
        who = await resolve_identity()
        data = await run_db(facts_service, who.household)
        return {**data, "speech": "Here is what your record shows."}
