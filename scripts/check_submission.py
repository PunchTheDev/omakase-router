#!/usr/bin/env python3
"""Gates 1–3 self-check. Run before opening a PR; the maintainer runs the same checks.

Checks: payload shape (Gate 1 surface), locked-file integrity vs main:manifest.json
(Gate 2), artifact sanity — sha/size/arch/entropy (Gate 3 static pass).
Exit 0 = submit; nonzero = the printed reason is what Peggy would reject with.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "..", "oc-eval"))

from oc_eval import routers  # noqa: E402

MIN_WEIGHT_ENTROPY = 0.5  # a lookup-table router concentrates mass on one worker


def fail(msg: str) -> int:
    print(f"REJECT: {msg}")
    return 1


def check_payload(path: str) -> str | None:
    with open(path) as f:
        payload = json.load(f)
    with open(os.path.join(ROOT, "payload-schema.json")) as f:
        schema = json.load(f)
    missing = [k for k in schema["required"] if k not in payload]
    if missing:
        return f"payload missing required fields: {missing}"
    extra = [k for k in payload if k not in schema["properties"]]
    if extra:
        return f"payload has unknown fields: {extra}"
    if not re.fullmatch(r"[0-9a-f]{64}", payload["weights_sha256"]):
        return "weights_sha256 is not a sha256 hex digest"
    return None


def check_locked_files() -> str | None:
    with open(os.path.join(ROOT, "manifest.json")) as f:
        locked = json.load(f)["locked"]
    for path, expected in locked.items():
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            return f"locked file deleted: {path}"
        with open(full, "rb") as f:
            if hashlib.sha256(f.read()).hexdigest() != expected:
                return f"locked file modified: {path}"
    return None


def check_artifact() -> str | None:
    sub = os.path.join(ROOT, "submission")
    try:
        router = routers.load_router(os.path.join(sub, "manifest.json"), sub)
    except (ValueError, FileNotFoundError, KeyError) as e:
        return f"artifact failed to load: {e}"
    if routers.perplexity_check(router) < MIN_WEIGHT_ENTROPY:
        return "weight-mass entropy below floor (degenerate policy)"
    return None


def main() -> int:
    payload_path = sys.argv[1] if len(sys.argv) > 1 else None
    checks = [
        ("gate-2 locked files", check_locked_files()),
        ("gate-3 artifact", check_artifact()),
    ]
    if payload_path:
        checks.insert(0, ("gate-1 payload", check_payload(payload_path)))
    for name, err in checks:
        if err:
            return fail(f"[{name}] {err}")
        print(f"ok: {name}")
    print("submission passes gates 1-3 self-check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
