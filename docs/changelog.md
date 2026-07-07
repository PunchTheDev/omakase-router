# Changelog / resets

All resets (split rotations, pool bumps, image bumps, router-pin bumps in
OC-H) are announced here before the Monday 00:00 UTC reset window they land in.

## 2026-07-07 — pool retune (pool.dev@v2) + OC-H contract v2

- Pool skills moderated + hedging confidence channel added (ignorant workers
  hedge 50% — the signal harness engineering exploits). Competition reset;
  champion retrained: 0.925, oracle capture 0.72.
- OC-H scoring contract v2: harnesses receive redacted task views, grading and
  cost metering are central, budgets enforced by the pool wrapper. Honest
  harnesses unaffected (main rescored unchanged at 0.933).
- OC-H gate split widened to 450 tasks (MDE ↓); champion-v2 router pinned.
- First OC-H merge: hedge-aware retry, Δ+3.6pp, p=3.1e-05 → major-delta.

## 2026-07-07 — competition genesis

- Pool `pool.dev@v1`: 5 mock workers with complementary profiles (dev mode).
- Suites: reasoning / math / code_qa, 40 tasks each, procedural.
- Seed champion: TinyRouter trained on dev-split solo baselines
  (`scripts/train_seed.py`) — deliberately beatable.
- Trust mode: `local-trusted` (dev). TDX path lands with the production pool.
