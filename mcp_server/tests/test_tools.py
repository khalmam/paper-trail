import pytest

from ledger.demo import DEMO_HOUSEHOLD
from ledger.models import Entry
from mcp_server.app import build_mcp


@pytest.mark.django_db(transaction=True)
async def test_log_issue_tool_writes_an_entry():
    mcp = build_mcp()
    await mcp.call_tool("log_issue", {"room": "Bedroom", "category": "leak", "description": "drip"})
    assert await Entry.objects.filter(household__name=DEMO_HOUSEHOLD).acount() == 1
