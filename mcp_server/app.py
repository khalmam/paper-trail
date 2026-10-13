from mcp.server.fastmcp import FastMCP

from .tools import (
    add_update, correct_entry, evidence_packet, issue_timeline, log_issue,
    record_landlord_contact, resolve_issue, set_deadline, verify_integrity, whats_open,
)

TOOL_MODULES = (
    log_issue, add_update, record_landlord_contact, set_deadline, resolve_issue,
    whats_open, issue_timeline, correct_entry, evidence_packet, verify_integrity,
)


def build_mcp() -> FastMCP:
    mcp = FastMCP("Paper Trail", stateless_http=True)
    for module in TOOL_MODULES:  # add new tool modules here
        module.register(mcp)
    return mcp
