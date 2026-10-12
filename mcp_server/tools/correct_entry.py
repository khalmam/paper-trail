from mcp.server.fastmcp import FastMCP

from ledger.domain.corrections import CorrectableField
from ledger.services import correct_entry as correct_service
from mcp_server.identity import resolve_identity
from mcp_server.runner import run_db

from ._common import entry_response


FIELD_WORDS = {
    "happened_on": "date it happened", "contacted_on": "date of contact",
    "deadline_date": "deadline date", "photo_ref": "photo note", "what": "promised action",
}


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def correct_entry(entry_number: int, field: CorrectableField, new_value: str,
                            reason: str = "") -> dict:
        """Fix a mistake in something already recorded, like a wrong date or room. entry_number
        is the number read out in the history. field is what to change and new_value is the
        right value, with dates like 2026-10-20. Nothing is erased: the original stays saved
        and the fix is added next to it. Use it only when the user says something was wrong.
        reason is why, in their words. Not legal advice."""
        who = await resolve_identity()
        entry = await run_db(
            correct_service, household=who.household, author=who.author,
            seq=entry_number, field=field, new_value=new_value, reason=reason,
        )
        speech = (f"Corrected the {FIELD_WORDS.get(field, field.replace('_', ' '))} on entry {entry_number}. "
                  f"The original is still saved, and the fix is entry {entry.seq}.")
        return entry_response(entry, speech)
