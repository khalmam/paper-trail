"""Who is calling? Stub for now. Replace with Alexa+ account-linking / token lookup."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Identity:
    household_name: str
    author: str


def resolve_identity() -> Identity:
    # TODO: derive from the authenticated MCP request once the auth path is known.
    return Identity(household_name="Demo household", author="dev-user")
