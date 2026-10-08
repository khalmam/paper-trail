from mcp.server.fastmcp import FastMCP

from ledger.services import verify_chain
from mcp_server.identity import resolve_identity
from mcp_server.runner import run_db


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def verify_integrity() -> dict:
        """Check that nothing in the user's evidence log has been changed, removed, or
        reordered since it was recorded. Use it when the user asks if their records are safe
        or untouched. If something was altered, it says exactly which entry."""
        who = await resolve_identity()
        r = await run_db(verify_chain, who.household)
        if r.ok:
            speech = f"Your evidence log checks out. All {r.verified} entries are intact."
        else:
            speech = f"{r.reason} {r.verified} earlier entries are intact."
        return {
            "ok": r.ok, "verified": r.verified, "bad_seq": r.bad_seq,
            "reason": r.reason, "last_verified_hash": r.head_hash, "speech": speech,
        }
