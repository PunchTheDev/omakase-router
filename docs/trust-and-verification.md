# Trust & verification

The trust model is deliberately simple and honest: **reproducibility from source
plus signed, published runtime logs.** No hardware attestation, no sealed
enclaves — the maintainer runs every evaluation on a trusted host and makes it
independently checkable. Every score on the dashboard links to a receipt that
proves what ran and lets you re-run it.

## What every receipt gives you

| Property | Mechanism | Verify it yourself |
|---|---|---|
| The run wasn't altered | maintainer **ed25519 signature** over the ledger entry's chain hash | recompute with the published pubkey (`omakase-maintainer/state/maintainer.pub.json`) |
| History wasn't rewritten | frontier log: append-only, **hash-chained**; each entry commits to the last | `omakase-eval verify-log runs/frontier.jsonl` |
| What the router did on every problem | the **per-task transcript** (each worker call, role, response, tokens, grading) is published and content-addressed | open `/runs/<sha>/tasks` or `GET /api/runs/<sha>/tasks` |
| The score is real | re-run from source: same split, same seed, same pool ⇒ same verdict | the reproduce command on each receipt |
| Only your artifact was scored | `manifest_sha256` / `weights_sha256` bound into the run + ledger entry | compare to your submission |
| Task order didn't favor anyone | options shuffled per-run by a seed you can't predict | inspect the transcript |

## The honest assumptions (read this)

1. **The maintainer runs evaluations honestly on a trusted host.** There is no
   TEE forcing this — trust rests on reproducibility (anyone with the pool can
   re-run and get the same verdict) and on the signed, published transcripts
   (any divergence is visible problem-by-problem).
3. **A live gate round is sealed, then opened.** The gate seed is secret while
   the round runs (it *is* the answer key: the generators are public), so gate
   seeds and gate transcripts are never published mid-round. The receipt still
   commits to the transcript's hash, so nothing can be rewritten after the fact.
   When the round retires, the seed is published and every receipt in it becomes
   independently reproducible. Verify a live round by its chain and signature;
   verify a retired round by re-running it.
2. **The worker pool serves what it claims.** Worker responses come from the
   pinned pool. The serving config is recorded; a degraded pool health-gates
   the queue rather than scoring. In dev the pool is a deterministic mock (a
   trusted component — see `omakase-eval/omakase_eval/mockpool.py`); production points at
   pinned vLLM endpoints over an egress allow-list.

## Why a Harness can't cheat

A Harness submission is arbitrary code, so it is not asked to behave — it is put
somewhere it *cannot* misbehave. `harness/` runs in an isolated child process
(`omakase_eval/sandbox.py`) whose only powers are two RPCs back to the scorer:

| Attack | Why it fails |
|---|---|
| import the answers and self-grade | `omakase_eval.suites` is not on the child's `sys.path` — `ModuleNotFoundError`. Reflection finds nothing to reflect into. |
| regenerate the hidden tasks | the gate seed is never sent to the child, and never written to a published blob or transcript |
| under-report cost / tokens | the parent meters the real pool calls; the child's claims are not read |
| exceed the budget | enforced in the parent on measured turns and tokens |
| exfiltrate the signing key | the child's environment is scrubbed; gate rounds run with no network, a read-only filesystem, and as `nobody`. Punch refuses to score a private split otherwise. |
| spoof a verdict on stdout | the child's stdout is `/dev/null`; the protocol rides private file descriptors |
| hang or crash the eval | wall-clock timeout per task; the child is killed and replaced, forfeiting that one task |

The `banned-primitive` static check runs first, but it is a cheap pre-filter, not
the boundary. A regex never was containment; the process boundary is.

### Integrity is checked against the maintainer, never the submission

Every check authenticates against data the maintainer holds, not data the miner
ships:

- **Locked files** are verified against the maintainer's own `manifest.json`, not
  the PR's. Editing a locked file and updating your own manifest hash to match no
  longer passes — the canonical hash comes from the maintainer's checkout.
- **The grader runs from the maintainer's tree.** The trusted `eval_adapter.py`
  scores the PR's `harness/` directory; the PR's copy of the adapter is never
  executed, so it can't declare itself the winner or read the seed.
- **Baselines and the incumbent** are read from the maintainer's checkout, and
  each carries a seed-fingerprint + pool-version + suite-version stamp that must
  match the round. A baseline shipped in the PR's `runs/` is ignored; an unstamped
  or mismatched one is refused.
- **Answers are graded exactly** — the final answer line must *be* the answer, not
  merely contain it, so returning a spray of every candidate answer wins nothing.
- The PR is materialized in an isolated worktree, so its files never overwrite the
  tree these checks read from.

## Verify a run yourself

```bash
# 1. the ledger chain is intact
omakase-eval verify-log omakase-router/runs/frontier.jsonl

# 2. the maintainer signature on any entry checks out (ed25519 over the entry sha)
#    — the dashboard does this live; the pubkey is published in the maintainer state

# 3. reproduce the verdict bit-for-bit
omakase-eval mockpool --port 8100 &
omakase-eval baselines --pool ../omakase-eval/configs/pool.dev.json --out /tmp/base.json
omakase-eval run --manifest submission/manifest.json --pool ../omakase-eval/configs/pool.dev.json \
        --baselines /tmp/base.json --split dev --seed 1

# 4. audit any problem: open /runs/<transcript_sha>/tasks/<task_id> on the dashboard
```

If you can't reproduce a published number, open an issue citing the run's `seq`
in the frontier log — one contested re-run per receipt is honored, and the
re-run is published whichever way it lands.

## Why cheating is negative-EV

- **Identity is real.** Punch verifies the sr25519 hotkey signature over your
  payload and that the hotkey is registered and GitHub-bound before any compute
  runs (Gate 1). A forged signature or unregistered hotkey is closed for free.
- **King of the hill.** Your router must beat the *current champion* with paired
  significance (McNemar), not just the best single worker — copying the champion
  earns nothing.
- **Variance farming loses.** 1 rerun / hotkey / 24h + credibility decay: a
  no-effect resubmitter hits the banlist long before a lucky pass. Losing a fair
  race barely dents credibility; a forged signature decays it fast.
- **Memorization doesn't transfer.** Gate splits use unpublished seeds and
  per-run option shuffling; production adds fresh-harvested tasks.
