#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True)


def get_version() -> str:
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover
        print("Python 3.11+ is required for tomllib")
        raise SystemExit(1)

    path = Path("pyproject.toml")
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    version = data.get("project", {}).get("version", "")
    if not isinstance(version, str) or not version.strip():
        print("Could not read [project].version from pyproject.toml")
        raise SystemExit(1)
    return version.strip()


def main() -> int:
    dry_run = "--dry-run" in sys.argv[1:]
    version = get_version()
    tag = version

    check = run("git", "rev-parse", "--verify", f"refs/tags/{tag}")
    if check.returncode == 0:
        print(f"Tag already exists: {tag}")
        return 1

    cmd = ["git", "tag", "-a", tag, "-m", f"Release {tag}"]
    if dry_run:
        print(f"Would run: {' '.join(cmd)}")
        return 0

    create = run(*cmd)
    if create.returncode != 0:
        stderr = create.stderr.strip()
        print(stderr or "Failed to create git tag")
        return create.returncode

    print(f"Created tag: {tag}")
    print(f"Push with: git push origin {tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
