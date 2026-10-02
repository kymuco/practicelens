# R0.5d — Alignment Substrate Ablation Results v1

Status: recorded machine-side ablation baseline

Frozen production revision:

`86a2714527facb2835856a8f0b54e1214b055525`

Machine-readable snapshot:

`docs/alignment_substrate_ablation_baseline_v1.json`

## Executive result

The strict narrow hypothesis is **supported** by two preregistered non-production profiles:

```text
current_positional_0p10
pitch_half_positional_0p10
```

Neither simple pitch reduction nor pitch removal succeeds.

The main timing defect identified in R0.5c is therefore demonstrably solvable **inside alignment-space**.

That result weakens the case for using pitch->timing cross-talk or local-timing non-monotonicity as evidence that PracticeLens must replace its frame-level representation.

It does **not** admit a production DTW change.

## Comparison

| Profile | pitch->timing max delta | local timing monotonicity | local timing endpoint delta | timing->pitch max delta | min coverage | strict hypothesis |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| `current` | 2.275722 | PARTIAL | -4.388514 | 0.763684 | 1.0 | no |
| `pitch_half` | 2.288083 | PARTIAL | -4.369139 | 0.894922 | 1.0 | no |
| `pitch_free_structural` | 5.018723 | PARTIAL | -4.349764 | 1.065332 | 1.0 | no |
| `current_positional_0p10` | 0.536953 | PASS | -1.609774 | 1.022111 | 1.0 | **yes** |
| `pitch_half_positional_0p10` | 0.773861 | PASS | -1.448789 | 1.228434 | 1.0 | **yes** |

Every profile preserves:

```text
pitch-drift directional sensitivity = PASS
pitch-drift monotonicity            = PASS
minimum alignment coverage          = 1.0
```

## Pitch reduction alone fails

### pitch_half

`pitch_half` does not improve the key defect:

```text
current pitch->timing max delta     2.275722
pitch_half pitch->timing max delta  2.288083
```

Local-timing monotonicity remains `PARTIAL`.

### pitch_free_structural

Removing pitch and voiced state entirely makes pitch-drift timing cross-talk substantially worse:

```text
pitch->timing max delta  5.018723
```

and local-timing monotonicity still remains `PARTIAL`.

This rejects the simple hypothesis:

> pitch is the problem, so remove pitch from DTW.

The alignment defect is not explained by pitch weight alone.

Energy/ZCR-only correspondence can wander even more under these synthetic targets.

## Positional regularization succeeds on the narrow timing defect

### current_positional_0p10

This profile keeps the exact current feature cost and adds only:

```text
0.10 * normalized positional distance
```

Pitch-drift timing cross-talk falls from:

```text
2.275722
->
0.536953
```

a reduction of approximately **76.4%**.

The local-timing sequence becomes:

```text
0 ms    100.000000
20 ms    99.348869
40 ms    99.154426
80 ms    98.390226
```

so:

```text
directional sensitivity = PASS
monotonicity            = PASS
```

The maximum warp-step fraction across target conditions also falls:

```text
current                  0.224561
current_positional_0p10  0.153285
```

Coverage remains 1.0.

This demonstrates that a weak geometric prior is sufficient to remove the specific non-monotonic path behavior exposed by R0.5c.

### pitch_half_positional_0p10

The combined half-pitch + positional profile also passes:

```text
pitch->timing max delta  0.773861
local timing monotonicity PASS
coverage                  1.0
```

But it does not outperform the simpler current-cost + positional profile on the primary cross-talk metric.

Therefore the ablation provides no evidence that reducing pitch dependence is necessary for solving this narrow defect.

## Important trade-off: timing response is compressed

The successful positional profile does not preserve the original timing response magnitude.

For `current_positional_0p10`:

```text
current 80 ms endpoint delta       -4.388514
positional 80 ms endpoint delta    -1.609774
```

The endpoint magnitude is reduced by about **63.3%**.

So positional regularization makes the path more orderly, but also makes the timing measurement less responsive.

This is why R0.5d cannot directly recommend a production change.

The strict hypothesis only required nonzero directional sensitivity and monotonicity; it deliberately did not invent a post-hoc magnitude threshold.

## Second trade-off: timing -> pitch residual grows

For the same successful profile:

```text
current timing->pitch max delta      0.763684
current_positional_0p10              1.022111
```

That is about 1.34x the current residual.

This is consistent with stronger positional regularization allowing less DTW compensation of the pre-alignment frame-boundary pitch effect found in R0.5c.

Again, the profile solves one alignment defect by exposing more of another already-known representation boundary.

## Architectural conclusion

R0.5d rules out a broad claim:

> the current timing defect proves that frame-level representation is insufficient.

It does not.

The main timing defect can be changed substantially by modifying alignment geometry alone.

The stronger conclusion is:

```text
timing measurement quality
depends on a trade-off between
    feature-driven correspondence
and
    geometric path regularity
```

The frame-level boundary effect behind timing->pitch remains a separate representation concern.

## What R0.5d eliminates

The experiment rejects:

- pitch removal as a sufficient fix;
- pitch-weight reduction as a sufficient fix;
- the claim that local-timing non-monotonicity is intrinsic to the timing score;
- the claim that the main timing defect necessarily requires event primitives.

It supports:

- positional path regularization as a causal lever;
- alignment-space as a viable solution family for the main timing defect.

## Recommended next machine-side experiment

Do **not** tune positional weights yet.

The next step should validate the already-preregistered simplest successful profile:

```text
current_positional_0p10
```

against the broader existing R0 evidence.

A suitable next experiment is **R0.5e — Alignment Candidate Validation v1**:

- rerun all R0.3 target and nuisance families with the candidate alignment;
- compare the unchanged current instrument and candidate counterfactual side by side;
- verify amplitude-gain invariance;
- inspect additive-noise behavior;
- preserve pitch-drift sensitivity and monotonicity;
- preserve/improve local-timing monotonicity;
- quantify the compressed timing response;
- quantify the larger timing->pitch residual;
- do not modify production DTW.

Only after that broader validation should a production alignment change even be considered.

## Human evidence boundary

R0.5b remains independent and still pending real local-session evidence.

The machine-side success in R0.5d does not establish that a 0.5-, 1-, or 2-point score movement is practically important for a musician.
