"""Fails when a layer imports something it must not, or a file grows past the size limit."""
import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCAN = ["config", "ledger", "mcp_server", "engine", "api", "scripts"]
MAX_LINES = 200
FORBIDDEN = {
    "ledger/domain": ["django", "mcp", "mcp_server", "engine", "api", "ledger.models", "ledger.services"],
    "engine": ["django", "mcp", "mcp_server", "api", "ledger.models", "ledger.services"],
    "ledger/models": ["mcp", "mcp_server", "api", "engine", "ledger.services"],
    "ledger/services": ["mcp", "mcp_server", "api"],
    "mcp_server": ["ledger.models"],
}


def source_files():
    for top in SCAN:
        for path in (ROOT / top).rglob("*.py"):
            rel = path.relative_to(ROOT)
            if "migrations" not in rel.parts:
                yield rel


def imported_modules(rel):
    for node in ast.walk(ast.parse((ROOT / rel).read_text())):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            yield node.module


FILES = sorted(source_files())


@pytest.mark.parametrize("rel", FILES, ids=str)
def test_layer_boundaries(rel):
    posix = rel.as_posix()
    if "tests" in rel.parts:
        return
    banned = [b for prefix, names in FORBIDDEN.items() if posix.startswith(prefix + "/") for b in names]
    bad = [(m, b) for m in imported_modules(rel) for b in banned if m == b or m.startswith(b + ".")]
    assert not bad, f"{posix} imports forbidden modules: {bad}"


@pytest.mark.parametrize("rel", FILES, ids=str)
def test_file_size(rel):
    assert len((ROOT / rel).read_text().splitlines()) <= MAX_LINES, f"{rel} is over {MAX_LINES} lines"
