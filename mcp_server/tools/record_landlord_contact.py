from mcp.server.fastmcp import FastMCP

from ledger.domain.vocab import ContactMethod
from ledger.services import record_landlord_contact as record_service
from mcp_server.identity import resolve_identity
from mcp_server.runner import run_db

from ._common import entry_response


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def record_landlord_contact(method: ContactMethod, note: str, room: str | None = None,
                                      contacted_on: str | None = None) -> dict:
        """Record that the user told their landlord or property manager about a problem.
        method is how: call, text, email, in_person, or letter. note is what was said or sent.
        room says which problem, like bedroom; leave it empty for the most recent one.
        contacted_on is an ISO date; leave it empty for today. Not legal advice."""
        who = await resolve_identity()
        entry = await run_db(
            record_service, household=who.household, author=who.author,
            method=method, note=note, room=room, contacted_on=contacted_on,
        )
        return entry_response(entry, f"Got it. I recorded your {method.replace('_', ' ')} to the landlord as entry {entry.seq}.")
