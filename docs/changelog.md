# Changelog / resets

All resets (split rotations, pool bumps, image bumps, router-pin bumps in
OC-H) are announced here before the Monday 00:00 UTC reset window they land in.

## 2026-07-07 — competition genesis

- Pool `pool.dev@v1`: 5 mock workers with complementary profiles (dev mode).
- Suites: reasoning / math / code_qa, 40 tasks each, procedural.
- Seed champion: TinyRouter trained on dev-split solo baselines
  (`scripts/train_seed.py`) — deliberately beatable.
- Trust mode: `local-trusted` (dev). TDX path lands with the production pool.
