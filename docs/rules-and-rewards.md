# Rules & rewards

## The crown (king of the hill)

- **champion** (multiplier 1.0): held by the PR currently at `submission/` on
  main. Streams SN74 emissions every epoch it is held. Dethroned = stream stops.
- **runner-up** (multiplier 0.15, max 2 concurrent): a PR that beat the
  *previous* champion baseline but lost the frontier race. Expires at the next
  champion change.
- A merged PR holding no label earns **nothing** (`default_label_multiplier: 0`).
  This competition pays for holding the frontier, not for having once won.
- The **Harness competition uses the identical rule**: its `champion` label is
  held by the last merged harness PR — any paired-significant in-band win takes
  it, regardless of delta size — until the next merge takes it.

## The bar

Your router must beat the current champion on a gate split with paired
significance (α = 0.05), without cost > +10% or latency p50 > +25% vs. champion.
The minimum detectable effect for the current suite size is published on the
dashboard — treat it as the real entry fee.

## Limits

| Rule | Value |
|---|---|
| Canonical reruns | 1 per hotkey per 24h (new PR resets the clock) |
| Open PRs | 1 per hotkey (second auto-closes the first) |
| Credibility | decays on mechanical failures; < 0.1 → banlist. Losing a fair Gate-4 race decays far slower than failing schema checks. |
| PR freeze | any edit after opening auto-closes |

## Honesty section

Most participants earn nothing most of the time — that is what king-of-the-hill
means. What you get for losing: the champion you failed to beat is public, your
receipt tells you exactly where you fell short, and the next gate split is two
integers away. The expected path to the crown is iterating on the public
champion, not lottery submissions.

## Resets

Gate-split rotations, pool version bumps, and router-pin bumps all land in
the **Monday 00:00 UTC reset window**, announced in [changelog](changelog.md)
beforehand. In-flight submissions caught by a reset re-run against the new
baseline, keeping their queue position.
