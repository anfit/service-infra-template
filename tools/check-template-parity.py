#!/usr/bin/env python3
"""Report drift between an infra repository and its template.

Usage: check-template-parity.py [--instance DIR] [--template DIR]

Defaults come from SERVICE_INFRA_DIR and SERVICE_INFRA_TEMPLATE_DIR. The tool is
informational: it lists files present in only one repository and shows which
shared generic files differ. Instance-specific content is expected to differ.
Exit status is 0 when only expected differences exist, 1 when generic files
that should match (GENERIC) differ or are missing.
"""
from __future__ import annotations

import argparse
import difflib
import os
import sys
from pathlib import Path

# Files that should be identical in the instance and the template.
GENERIC = [".gitignore", "tools/check-template-parity.py"]
# Files that exist in both but are expected to differ (instance data).
EXPECTED_DIFF = ["README.md", "hosts/prod.yaml"]
# Top-level areas whose files are instance data by nature.
INSTANCE_ONLY_PREFIXES = ("deployments/", "configs/", "hosts/", "docs/")
# Files the instance should mirror from the template in shape, not content.
SHAPE_FILES = [".env.example"]


def tracked(root: Path) -> set[str]:
    import subprocess

    out = subprocess.run(
        ["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True
    ).stdout
    return {line.strip() for line in out.splitlines() if line.strip()}


def read(root: Path, rel: str) -> list[str]:
    return (root / rel).read_text(encoding="utf-8").replace("\r\n", "\n").splitlines()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--instance", type=Path, default=os.environ.get("SERVICE_INFRA_DIR"))
    ap.add_argument("--template", type=Path, default=os.environ.get("SERVICE_INFRA_TEMPLATE_DIR"))
    args = ap.parse_args()
    if not args.instance or not args.template:
        print("error: set SERVICE_INFRA_DIR and SERVICE_INFRA_TEMPLATE_DIR or pass flags", file=sys.stderr)
        return 2
    inst, tmpl = Path(args.instance), Path(args.template)
    a, b = tracked(inst), tracked(tmpl)
    failed = False

    print("Generic files that must match:")
    for rel in GENERIC:
        if rel not in a or rel not in b:
            print(f"  MISSING  {rel} (instance={rel in a}, template={rel in b})")
            failed = True
        elif read(inst, rel) != read(tmpl, rel):
            print(f"  DIFFERS  {rel}")
            for line in difflib.unified_diff(read(tmpl, rel), read(inst, rel), "template", "instance", lineterm="", n=1):
                print("    " + line)
            failed = True
        else:
            print(f"  ok       {rel}")

    print("\nShape files the instance should also have:")
    for rel in SHAPE_FILES:
        print(f"  {'ok' if rel in a else 'ABSENT':8} {rel}  (instance)")

    only_t = sorted(f for f in b - a if f not in EXPECTED_DIFF and not f.startswith(INSTANCE_ONLY_PREFIXES))
    only_i = sorted(f for f in a - b if f not in EXPECTED_DIFF and not f.startswith(INSTANCE_ONLY_PREFIXES))
    print("\nOnly in template (consider adding to the instance):")
    print("\n".join(f"  {f}" for f in only_t) or "  none")
    print("\nOnly in instance, outside instance-data areas (consider upstreaming):")
    print("\n".join(f"  {f}" for f in only_i) or "  none")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
