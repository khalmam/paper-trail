"""Who is calling? Bearer token -> Member. Dev fallback only when MCP_DEV_IDENTITY is on."""
from dataclasses import dataclass
from typing import Any

from django.conf import settings

from ledger.demo import DEMO_HOUSEHOLD, DEV_AUTHOR
from ledger.services import authenticate_token, get_or_create_household

from .context import bearer_token
from .runner import run_db


@dataclass(frozen=True)
class Identity:
    household: Any  # a ledger Household; typed Any so this adapter never imports ledger.models
    author: str
    role: str


async def resolve_identity() -> Identity:
    token = bearer_token.get()
    if token:
        member = await run_db(authenticate_token, token)
        if member is None:
            raise PermissionError("That access token is not recognized.")
        return Identity(member.household, member.display_name, member.role)
    if getattr(settings, "MCP_DEV_IDENTITY", False):
        household = await run_db(get_or_create_household, DEMO_HOUSEHOLD)
        return Identity(household, DEV_AUTHOR, "owner")
    raise PermissionError("Missing access token.")
