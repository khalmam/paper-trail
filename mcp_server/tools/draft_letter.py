from mcp.server.fastmcp import FastMCP

from ledger.services import draft_letter as draft_service
from mcp_server.identity import resolve_identity
from mcp_server.runner import run_db


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def draft_letter(room: str | None = None) -> dict:
        """Write a draft letter to the landlord about an open problem, using only what is in the
        user's record. It saves nothing and sends nothing: the user reviews it and sends it
        themselves. room says which problem, like bedroom; leave it empty for the most recent
        open one. Not legal advice."""
        who = await resolve_identity()
        letter = await run_db(draft_service, who.household, room)
        return {**letter.to_dict(),
                "speech": "I wrote a draft letter from your record. Review it, fill in the bracketed "
                          "parts and send it yourself, then tell me once it is sent."}
