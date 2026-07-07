# Trust & verification

Every score on the dashboard links to a run receipt. This page says exactly
what a receipt proves, what it assumes, and how to check it yourself.

## What is cryptographically bound

| Property | Mechanism |
|---|---|
| What code + model scored you | digest-pinned runtime image (TDX MRTD in production) |
| Your exact artifact was evaluated | `weights_sha256` bound into the run blob |
| No external model calls during eval | egress allow-list = pool endpoints only (attested in TDX mode) |
| History wasn't rewritten | frontier log: append-only hash chain; any edit breaks every later entry |
| Task order / options weren't chosen to favor anyone | shuffle seed = PR HEAD SHA (unknowable pre-submission) |

## What is honestly assumed (read this)

1. **The worker pool serves what it claims.** Worker responses come from our
   pinned vLLM cluster, *outside* the sealed enclave. The serving config
   (model shas, sampling params) is hashed into every run blob and the pool is
   health-gated before any scoring run — but you are trusting the operator not
   to bias serving. Roadmap: attested serving. Until then this is the largest
   trust assumption in the system, and we'd rather name it than hide it.
2. **Trust mode is per-run.** Receipts state `tdx` (hardware quote, verify
   against Intel collateral) or `local-trusted` (maintainer-run, reproducible
   from source — the sparkinfer posture). Dev mode is always `local-trusted`.

## Verify a run yourself

```bash
oc-eval verify-log runs/frontier.jsonl                  # chain integrity
# reproduce any dev-mode run bit-for-bit:
oc-eval mockpool --port 8100 &
oc-eval baselines --pool ../oc-eval/configs/pool.dev.json --out /tmp/base.json
oc-eval run --manifest submission/manifest.json --pool ../oc-eval/configs/pool.dev.json \
        --baselines /tmp/base.json --split dev --seed 1
```

Same split, same seed, same image ⇒ same verdict. If you can't reproduce a
published number, open an issue citing the run's `seq` in the frontier log —
one contested re-run per receipt is honored, and the re-run is published
whichever way it lands.

## Why cheating is negative-EV, with numbers

Variance farming: at α=0.05 a no-effect submission passes by luck once per ~20
attempts; at 1 rerun/24h with credibility decay per failure, the banlist
arrives first. Answer memorization: gate seeds are unpublished and rotated,
and option order is reshuffled per run — a memorized dev split scores at
chance on the letters it memorized. Phoning a frontier model: the eval
environment can only reach the pool endpoints.
