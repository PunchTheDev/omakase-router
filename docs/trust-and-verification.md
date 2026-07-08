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
   (any divergence is visible problem-by-problem). This is the same posture
   sparkinfer runs on, stated plainly.
2. **The worker pool serves what it claims.** Worker responses come from the
   pinned pool. The serving config is recorded; a degraded pool health-gates
   the queue rather than scoring. In dev the pool is a deterministic mock (a
   trusted component — see `omakase-eval/omakase_eval/mockpool.py`); production points at
   pinned vLLM endpoints over an egress allow-list.

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
