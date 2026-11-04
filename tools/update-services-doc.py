#!/usr/bin/env python3
"""Refresh the generated deployment inventory in docs/services.md.

The inventory is produced offline by `vps-deployer list --format markdown` and
written between BEGIN/END markers; hand-written content in the file is untouched.
If the markers are absent, a new "Generated inventory" section is appended.

Usage: update-services-doc.py [--repo DIR] [--deployer CMD] [--check]

--check changes nothing and exits 1 when the file is out of date (for CI).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

BEGIN = "<!-- BEGIN GENERATED INVENTORY (tools/update-services-doc.py) -->"
END = "<!-- END GENERATED INVENTORY -->"
HEADING = "## Generated inventory"
NOTE = ("Generated from the manifests; do not edit between the markers. "
        "Regenerate with `python tools/update-services-doc.py`.")


def render(repo: Path, deployer: str) -> str:
    result = subprocess.run([deployer, "--repo", str(repo), "list", "--format", "markdown"],
                            capture_output=True, text=True)
    if result.returncode:
        sys.exit(f"error: `{deployer} list` failed:\n{result.stderr or result.stdout}")
    return result.stdout.strip()


def update(text: str, table: str) -> str:
    block = f"{BEGIN}\n{table}\n{END}"
    if BEGIN in text and END in text:
        head, rest = text.split(BEGIN, 1)
        _, tail = rest.split(END, 1)
        return head + block + tail
    return f"{text.rstrip()}\n\n{HEADING}\n\n{NOTE}\n\n{block}\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", type=Path, default=Path(os.environ.get("SERVICE_INFRA_DIR", ".")))
    ap.add_argument("--deployer", default="vps-deployer")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    doc = args.repo / "docs" / "services.md"
    current = doc.read_text(encoding="utf-8") if doc.is_file() else "# Managed services\n"
    new = update(current.replace("\r\n", "\n"), render(args.repo, args.deployer))
    if new == current.replace("\r\n", "\n"):
        print("services.md is up to date")
        return 0
    if args.check:
        print("services.md is out of date; run tools/update-services-doc.py")
        return 1
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text(new, encoding="utf-8", newline="\n")
    print(f"updated {doc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
