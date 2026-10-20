from mcp.server.fastmcp import FastMCP

from ledger.domain.vocab import ContactMethod
from ledger.services import confirm_letter_sent as confirm_service
from mcp_server.identity import resolve_identity
from mcp_server.runner import run_db

from ._common import entry_response


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def confirm_letter_sent(method: ContactMethod = "letter", room: str | None = None,
                                  sent_on: str | None = None) -> dict:
        """Record that the user actually sent the letter. Use it only after the user says they
        sent it; a draft alone is never recorded. method is how it went: letter, email, or
        in_person. sent_on is an ISO date; leave it empty for today. Not legal advice."""
        who = await resolve_identity()
        entry = await run_db(confirm_service, household=who.household, author=who.author,
                             method=method, room=room, sent_on=sent_on)
        return entry_response(entry, f"Recorded that your letter was sent, entry {entry.seq}.")
