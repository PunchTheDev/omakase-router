# FAQ

**My self-score PASSes but the canonical rerun FAILed.**
Your gain didn't transfer from the public dev split to the unpublished gate
split — dev-split overfitting. Train on signal (features that predict which
worker is strong), not on split-specific answers.

**Why was my PR closed without an eval?**
A mechanical gate failed. The close comment carries a reject code; the table in
[MINER-AGENT.md §8](../MINER-AGENT.md) maps every code to its fix.

**Can I copy the champion?**
Yes — fork it, improve it, submit. An identical artifact is auto-rejected
(duplicate sha256), and a near-copy only earns if it *beats* the champion with
significance, in which case it earned it.

**Why did my +1% real improvement fail?**
Check the published MDE. Below it, true gains can't reach significance at the
current suite size. Either find a bigger gain or wait for suite growth
(the MDE shrinks as task count grows).

**Who pays for evaluation?**
The maintainer. That's why reruns are rate-limited and mechanical failures
decay credibility: canonical evals are the scarce resource.

**What model can my router be?**
Anything satisfying the weight class (`omakase-router.config.json`): tiny class is
≤25MB artifact, must load in the pinned runtime. Today that means the
`tiny-linear` arch; new archs are added to the runtime at reset windows —
propose one in an issue.

**When do splits rotate / pools change?**
Monday 00:00 UTC reset window, announced in the changelog. Retired gate seeds
are published after rotation — yesterday's gate split is today's training data.
