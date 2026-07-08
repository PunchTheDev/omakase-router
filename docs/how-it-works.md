# How the Router competition works

**The idea.** No single model is best at everything. A pool of open-weights
specialists plus a tiny learned router can beat any one of them — at lower
cost. The Router competition is a permissionless race to find that router.

**The loop.**

```
 miner trains router ──► PR (weights manifest only)
        │                     │
        │              Punch gates 1-3 (identity, locked files, static checks)
        │                     │
        │              FIFO queue ──► Gate 4: canonical rerun (trusted host)
        │                     │        paired vs. current champion on a gate split
        │                     │
        │        PASS: merge ──► champion label ──► SN74 emissions stream
        │        FAIL: close with the verdict blob
        └── champion weights are public: fork them and go again
```

**What's fixed:** the worker pool (pinned model revisions), the harness (turn
loop, role prompts, budgets), the suites, the scoring function. **What you
control:** the weights. That split is what makes it a policy competition.

**Scoring.** Accuracy is gated: your router must beat the champion with
statistical significance (paired McNemar on identical tasks and seeds). Cost
and latency are guards: +10%/+25% tolerance bands. `oracle capture` — how much
of the pool's theoretical routing headroom the champion extracts — is the
health metric of the whole competition; when it plateaus near 1.0, the pool or
weight class gets refreshed.

**Why you can't cheat (short version).** Your hotkey signature is verified and
your identity chain-checked before any compute runs, you must beat the *current
champion* (not just the best worker), gate splits use unpublished seeds, options
are shuffled per-run, results are hash-chained and maintainer-signed in the
frontier log, and every run publishes a full per-task transcript you can audit
problem-by-problem. Full detail: [trust-and-verification](trust-and-verification.md).
