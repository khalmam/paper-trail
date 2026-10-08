from mcp.server.fastmcp import FastMCP

from .tools import add_update, log_issue, verify_integrity


def build_mcp() -> FastMCP:
    mcp = FastMCP("Paper Trail", stateless_http=True)
    for module in (log_issue, add_update, verify_integrity):  # add new tool modules here
        module.register(mcp)
    return mcp
