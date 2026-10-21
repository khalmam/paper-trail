import os

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from .tools import (
    add_update, confirm_letter_sent, correct_entry, draft_letter, evidence_packet, issue_timeline, log_issue,
    record_landlord_contact, resolve_issue, set_deadline, verify_integrity, whats_open,
)

TOOL_MODULES = (
    log_issue, add_update, record_landlord_contact, set_deadline, resolve_issue,
    whats_open, issue_timeline, correct_entry, evidence_packet, verify_integrity,
    draft_letter, confirm_letter_sent,
)


def build_mcp() -> FastMCP:
    extra = [h.strip() for h in os.environ.get("MCP_ALLOWED_HOSTS", "").split(",") if h.strip()]
    hosts = ["127.0.0.1", "127.0.0.1:*", "localhost", "localhost:*"]
    hosts += [h for e in extra for h in (e, f"{e}:*")]
    mcp = FastMCP(
        "Paper Trail", stateless_http=True,
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=True, allowed_hosts=hosts,
            allowed_origins=[f"http://{h}" for h in hosts] + [f"https://{h}" for h in hosts],
        ),
    )
    for module in TOOL_MODULES:  # add new tool modules here
        module.register(mcp)
    return mcp
