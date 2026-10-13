from mcp.server.fastmcp import FastMCP

from ledger.services import evidence_packet as packet_service
from mcp_server.identity import resolve_identity
from mcp_server.runner import run_db


def _plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def evidence_packet(room: str | None = None) -> dict:
        """Put together the full evidence packet: every problem with its history, deadlines,
        landlord contacts, how complete the record is, repeat problems, any disagreements
        between roommates, and a check that nothing was altered. Use it when the user wants
        everything in one place to keep or show someone. room limits it to one problem, like
        bedroom; leave it empty for all. It describes what the household reported and is not
        legal advice."""
        who = await resolve_identity()
        result = await run_db(packet_service, who.household, room)
        issues = result.packet.issues
        open_count = sum(1 for i in issues if i.summary.status == "open")
        if result.integrity.ok:
            lead = f"Your record checks out, all {_plural(result.entry_count, 'entry').replace('entrys', 'entries')} intact."
        else:
            lead = (f"Warning: {result.integrity.reason} The packet is still listed below, "
                    f"but treat it with care.")
        if issues:
            body = f" The packet covers {_plural(len(issues), 'problem')}, {open_count} still open."
        else:
            body = " There is nothing to put in a packet yet."
        return {**result.to_dict(), "speech": lead + body}
