"""Every package folder that holds Python modules needs an __init__.py."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ["config", "ledger", "mcp_server", "engine", "ai", "api"]


def test_every_package_folder_has_init():
    missing = []
    for top in PACKAGES:
        for folder in [ROOT / top, *(p for p in (ROOT / top).rglob("*") if p.is_dir())]:
            if "__pycache__" in folder.parts:
                continue
            if any(folder.glob("*.py")) and not (folder / "__init__.py").exists():
                missing.append(str(folder.relative_to(ROOT)))
    assert not missing, f"missing __init__.py in: {missing}"
