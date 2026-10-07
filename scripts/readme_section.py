"""Replace the text between <!-- NAME:START --> and <!-- NAME:END --> in README.md.
Usage: python scripts/readme_section.py STATUS path/to/new_text.md
"""
import re
import sys
from pathlib import Path

name, src = sys.argv[1], Path(sys.argv[2]).read_text().strip()
readme = Path("README.md")
pattern = re.compile(rf"(<!-- {name}:START -->\n).*?(\n<!-- {name}:END -->)", re.S)
text = readme.read_text()
if not pattern.search(text):
    sys.exit(f"markers for {name} not found")
readme.write_text(pattern.sub(lambda m: m.group(1) + src + m.group(2), text))
print(f"updated {name}")
