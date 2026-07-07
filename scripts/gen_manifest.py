#!/usr/bin/env python3
"""Regenerate manifest.json — the Gate 2 authority listing every locked file's sha256.

Maintainer-only; run after any deliberate change to locked surface, never by miners.
Everything in the repo is locked except submission/ and runs/.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess

UNLOCKED_PREFIXES = ("submission/", "runs/")


def main() -> int:
    root = os.path.join(os.path.dirname(__file__), "..")
    files = subprocess.run(["git", "-C", root, "ls-files"], capture_output=True, text=True, check=True).stdout.split()
    locked = {}
    for path in sorted(files):
        if path == "manifest.json" or path.startswith(UNLOCKED_PREFIXES):
            continue
        with open(os.path.join(root, path), "rb") as f:
            locked[path] = hashlib.sha256(f.read()).hexdigest()
    with open(os.path.join(root, "manifest.json"), "w") as f:
        json.dump({"locked": locked}, f, indent=1, sort_keys=True)
    print(f"manifest.json: {len(locked)} locked files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
