#!/usr/bin/env python3
"""Train the seed champion: a TinyRouter fit to solo-baseline labels on the dev split.

This is the beatable starting point every miner improves on. Usage:
    python scripts/train_seed.py --pool ../oc-eval/configs/pool.dev.json
Requires the mock pool to be up (oc-eval mockpool --port 8100).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "oc-eval"))

from oc_eval import baselines as bl  # noqa: E402
from oc_eval import routers, suites  # noqa: E402
from oc_eval.workers import Pool  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=True)
    ap.add_argument("--split", default="dev")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out-dir", default=os.path.join(os.path.dirname(__file__), "..", "submission"))
    args = ap.parse_args()

    pool = Pool.from_config(args.pool)
    base = bl.compute(pool, args.split, args.seed)
    workers = list(pool.workers)
    tasks = sorted(suites.generate_split(args.split, args.seed), key=lambda t: t.id)
    prompts = [t.prompt for t in tasks if t.id in base.best_worker_per_task]
    labels = [workers.index(base.best_worker_per_task[t.id]) for t in tasks if t.id in base.best_worker_per_task]

    router = routers.fit_tiny_router(prompts, labels, workers, seed=0)
    weights_path = os.path.join(args.out_dir, "weights.json")
    router.save(weights_path)

    manifest = {
        "arch": "tiny-linear",
        "weights_file": "weights.json",
        "weights_sha256": routers.sha256_file(weights_path),
        "size_bytes": os.path.getsize(weights_path),
        "trained_on": {"split": args.split, "seed": args.seed},
    }
    with open(os.path.join(args.out_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"seed champion written: {weights_path} (sha {manifest['weights_sha256'][:12]}…)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
