from mcp.server.fastmcp import FastMCP

from .tools import log_issue


def build_mcp() -> FastMCP:
    mcp = FastMCP("Paper Trail", stateless_http=True)
    for module in (log_issue,):  # add new tool modules here
        module.register(mcp)
    return mcp
