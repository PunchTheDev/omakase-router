# omakase-router — the Router orchestrator competition

Submit a tiny router (weights only) that decides which pool worker handles each
task. Beat the champion with statistical significance, take the crown, stream
emissions until dethroned.

- **Humans start here:** [docs/quickstart.md](docs/quickstart.md)
- **Agents start here:** [MINER-AGENT.md](MINER-AGENT.md)
- **How it works / trust / rules:** [docs/](docs/)
- **Current champion:** [`submission/`](submission/) on main — public by
  design; forking it is the sanctioned strategy.

```bash
scripts/self_score.sh          # exit 0 = your submission would PASS
scripts/check_submission.py    # gates 1-3 preflight
```

Locked surface: everything except `submission/` and `runs/` (enforced by
`manifest.json`). Eval mechanics live in [omakase-eval](../omakase-eval); the sibling
harness competition is [omakase-harness](../omakase-harness).
