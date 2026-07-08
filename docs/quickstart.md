# Miner quickstart (human)

Agent operator? Hand your agent [MINER-AGENT.md](../MINER-AGENT.md) instead —
it is the same procedure written for machines.

```bash
# one-time setup (dev mode: skip the two btcli/gitt steps)
btcli wallet create && btcli subnet register --netuid 74
gitt miner post <github-pat>                     # bind GitHub ↔ hotkey
git clone <this-repo> && cd omakase-router
python3 -m venv ../omakase-eval/.venv && ../omakase-eval/.venv/bin/pip install -e ../omakase-eval

# iterate
python3 scripts/train_seed.py --pool ../omakase-eval/configs/pool.dev.json   # or your own trainer
scripts/self_score.sh                            # exit 0 = you beat the bar locally

# submit
scripts/check_submission.py                      # gates 1-3 preflight
# open a PR touching only submission/, with the payload block from payload-schema.json
```

Strategy notes:

- **Fork the champion.** `submission/` on main is the current best router,
  public by design. Starting from zero is a handicap you choose.
- The dev split is public; gate splits are the same generators with
  unpublished seeds. Real signal transfers, memorized answers don't.
- Mind the MDE printed by self-score: below it, real gains still fail.
- One canonical rerun per 24h — self-score until you're confident, then spend it.
