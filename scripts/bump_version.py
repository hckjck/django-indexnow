#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/bump_version.py x.y.z[-suffix]")
        return 1

    version = sys.argv[1].strip()
    if not re.match(r"^\d+\.\d+\.\d+([.-][0-9A-Za-z]+)?$", version):
        print("Invalid VERSION format. Expected x.y.z or x.y.z-suffix")
        return 1

    files = {
        Path("pyproject.toml"): (
            r'^version\s*=\s*"[^\"]+"$',
            f'version = "{version}"',
        ),
        Path("indexnow/__init__.py"): (
            r'^__version__\s*=\s*"[^\"]+"$',
            f'__version__ = "{version}"',
        ),
    }

    for path, (pattern, replacement) in files.items():
        original = path.read_text(encoding="utf-8")
        updated, count = re.subn(pattern, replacement, original, flags=re.MULTILINE)
        if count != 1:
            print(f"Could not update version in {path}")
            return 1
        path.write_text(updated, encoding="utf-8")

    print(f"Bumped version to {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
