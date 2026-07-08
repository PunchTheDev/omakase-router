# MINER-AGENT.md — Router machine-first mining spec

You are an agent mining the **Router competition** (orchestrator routing). Follow this
document exactly. Never guess schemas or invent steps. When you reach a HUMAN
step, stop and ask your operator.

## 0. The game in three sentences

A fixed pool of worker LLMs answers benchmark tasks. Your submission is a tiny
router (weights only, ≤25MB artifact) that decides, per task, which worker to
call. You win by beating the current champion's accuracy with statistical
significance, without regressing cost (>+10%) or latency (>+25%).

## 1. Prerequisites

| Step | Who | Command / action |
|---|---|---|
| 1a. Bittensor wallet + hotkey | **HUMAN** | `btcli wallet create` |
| 1b. Register on SN74 (costs TAO) | **HUMAN** | `btcli subnet register --netuid 74` |
| 1c. Bind GitHub ↔ hotkey | **HUMAN** | `gitt miner post <github-pat>` (das-gittensor binding) |
| 1d. Clone + install | agent | `git clone <this repo> && cd omakase-router && python3 -m venv ../omakase-eval/.venv && ../omakase-eval/.venv/bin/pip install -e ../omakase-eval` |

Dev mode (no chain): skip 1a–1c; PRs are gated locally with a stub identity.

## 2. Build a router

The submission contract (`submission/manifest.json`):

```json
{
  "arch": "tiny-linear",
  "weights_file": "weights.json",
  "weights_sha256": "<sha256 of weights.json>",
  "size_bytes": 123456,
  "trained_on": {"split": "dev", "seed": 1}
}
```

- Only files under `submission/` may change. Everything else is hash-locked
  (Gate 2 checks against `main:manifest.json` — the copy on main, not yours).
- `arch` must be one the pinned runtime supports (`tiny-linear` today; see
  `omakase-router.config.json → weight_class` for size caps).
- The current champion is `submission/` on main. **Forking the champion is the
  sanctioned strategy** — improve it, don't start from zero.
- Training signal: `omakase-eval baselines` gives per-worker solo accuracy and the
  per-task best-worker table. `omakase_eval.routers.fit_tiny_router` is a working
  reference trainer (see `scripts/train_seed.py`).

## 3. Self-score (iterate here until you beat the bar)

```bash
scripts/self_score.sh            # exit 0 = would PASS the canonical rerun
```

Reads: current MDE (minimum detectable effect) is printed in the run blob —
gains below it will not reach significance no matter how real they are. The
dev split is public and identical in distribution to gate splits; gate splits
use unpublished seeds, so memorizing dev answers does not transfer.

## 4. Pre-submission check

```bash
scripts/check_submission.py [payload.json]   # gates 1-3, same checks Punch runs
```

Fix every `REJECT:` before opening a PR. A PR that fails mechanical gates costs
you your 24h rerun slot and decays credibility.

## 5. Open the PR

- Branch from current main. Diff must touch only `submission/`.
- PR body must contain exactly one fenced JSON block matching
  `payload-schema.json`. Prose outside it carries zero weight with the
  maintainer — write for humans, but never rely on it.
- Sign: `signature = hotkey_sign(sha256("omakase-router|<hotkey>|<weights_sha256>"))`.
- **Do not edit the PR after opening.** Any change between gate-walk and merge
  auto-closes it (freeze rule). Open a fresh PR instead.

## 6. What happens next

1. Punch walks gates 1–3 (minutes). Mechanical failure → close + reason code.
2. Canonical rerun queues (pure FIFO; position visible on the dashboard).
3. Gate 4 reruns your router on a gate split, paired against main's champion.
4. PASS → merge; you take the `champion` label and its emission stream until
   dethroned. Near-miss that still beats the previous baseline → `runner-up`.
5. FAIL → close with the verdict blob; your self-score telling you PASS but
   canonical saying FAIL usually means dev-split overfitting.

## 7. Limits (exceeding any of these is negative-EV by design)

- 1 canonical rerun per hotkey per 24h; a new PR resets the clock.
- 1 open PR per hotkey; opening a second auto-closes the first.
- Repeated mechanical failures decay credibility; below 0.1 → banlist.

## 8. Reject codes → corrective action

| Code | Meaning | Fix |
|---|---|---|
| `payload-malformed` | body JSON fails schema | validate against `payload-schema.json` |
| `identity-unbound` | hotkey↔GitHub binding missing | HUMAN step 1c |
| `locked-file-modified` | diff outside `submission/` | rebase, touch only `submission/` |
| `artifact-sha-mismatch` | manifest sha ≠ weights file | recompute `weights_sha256` |
| `artifact-degenerate` | entropy floor (lookup-table policy) | train a real policy |
| `not-significant` | gain below the bar on gate split | improve real accuracy; check MDE |
| `cost-regression` / `latency-regression` | axes outside tolerance | route cheaper/faster |
| `frozen-pr-changed` | you edited after opening | open a fresh PR |
