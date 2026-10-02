# R0.5c — Cross-Talk Attribution Results v1

Status: recorded machine-side attribution baseline

Frozen production revision:

`03edfe96046b1ccb86b58dc4275634b9caf62396`

Machine-readable snapshot:

`docs/cross_talk_attribution_baseline_v1.json`

## Executive result

The remaining R0.4 protected-dimension movements do **not** share one common cause.

```text
pitch drift -> rhythm_fidelity
    pre-alignment onset/time representation

pitch drift -> timing_consistency
    DTW alignment path

local timing warp -> pitch_fidelity
    mixed, but begins before DTW at frame-level pitch
    DTW mostly compensates rather than creates it
```

This substantially narrows the R0.6 architecture question.

## Pitch drift -> timing consistency

Observed maximum protected-score movement:

```text
2.275722 points
```

Counterfactual linear-alignment movement:

```text
0.000000 points
```

Maximum alignment contribution:

```text
2.275722 points
```

Attribution:

```text
alignment_path
```

This is a strong localization result.

The timing score does not directly consume pitch values. Under a relative-position alignment it remains exactly 100 across the entire pitch-drift series.

The movement appears only when the production feature-similarity DTW path is used.

Current DTW local cost is dominated by pitch:

```text
pitch   0.55
energy  0.25
ZCR     0.20
+ voiced mismatch penalty
```

So a pitch perturbation changes the alignment path, and the timing score then interprets that changed path as timing movement.

### Architectural implication

The observed pitch -> timing cross-talk is **not evidence that timing requires a new event representation**.

It is first evidence that the alignment substrate currently mixes the construct being measured with the coordinate system used to measure timing.

A narrower alignment experiment should come before a representation rewrite.

## Why timing monotonicity failed in R0.4

For local timing warp, the observed mean normalized DTW position error is:

```text
0 ms   0.000000
20 ms  0.006736
40 ms  0.003177
80 ms  0.006583
```

The corresponding timing scores are:

```text
0 ms   100.000
20 ms   95.509
40 ms   97.882
80 ms   95.611
```

The score formula itself is monotonic in mean position error.

The non-monotonicity therefore originates upstream: the DTW path for the 40 ms perturbation is geometrically closer to the diagonal than the path for 20 ms.

This explains the previous R0.4 `PARTIAL` monotonicity result without changing or tuning the score.

## Pitch drift -> rhythm fidelity

Observed maximum movement:

```text
0.013356 points
```

Linear-alignment movement:

```text
0.013356 points
```

Alignment contribution:

```text
0.000000 points
```

Attribution:

```text
pre_alignment_feature_or_score_path
```

The dependency graph makes this more specific:

`rhythm_fidelity` consumes onset times and the time axis and does not consume DTW alignment or pitch scores.

The onset count remains constant:

```text
23 -> 23
```

and the tempo estimate remains unchanged.

But normalized onset nearest-distance changes slightly:

```text
0
0
0.000007123
0.000021369
```

Therefore the tiny rhythm movement already exists in the extracted onset/time representation.

### Architectural implication

This is not an alignment problem and not evidence for a broad representation rewrite.

Its magnitude is extremely small in the synthetic audit. R0.5b human/session evidence should determine whether it matters at all before engineering work is spent on it.

## Local timing warp -> pitch fidelity

Observed maximum protected-score movement:

```text
0.763684 points
```

Under counterfactual linear alignment, pitch movement is much larger:

```text
3.817713 points
```

Maximum alignment contribution:

```text
3.054029 points
```

Attribution:

```text
mixed_pre_alignment_and_alignment
```

The important direction is that DTW is **reducing**, not creating, most of this cross-talk.

Before DTW, relative-position frame comparison already sees pitch errors:

```text
20 ms warp  5.698 cents mean error
40 ms warp  3.516 cents mean error
80 ms warp  7.635 cents mean error
```

Voiced coverage remains unchanged.

This is consistent with frame windows crossing a moved note/event boundary: the musical frequencies are unchanged by construction, but which local waveform content falls inside a fixed frame changes near transitions.

### Architectural implication

This is the first R0 evidence that specifically supports investigating a boundary-aware or transition/event representation.

It does **not** yet justify replacing the full frame-level system.

The observed production cross-talk is only 0.764 points because DTW compensates most of the pre-alignment boundary effect.

R0.5b remains necessary to tell us whether that residual is even large relative to ordinary human within-session variation.

## What R0.5c eliminates

The audit rules out several broad explanations:

- pitch -> timing is not caused by the timing score directly reading pitch;
- pitch -> timing is not present under alignment-independent relative-position mapping;
- timing -> pitch is not primarily created by DTW;
- pitch -> rhythm is not caused by DTW;
- component scores are not feeding each other.

The current defects therefore should not be treated as one generic "frame representation is bad" problem.

## Narrowed architecture map

```text
pitch drift
    |
    +--> onset/time feature micro-movement
    |       -> tiny rhythm cross-talk
    |
    +--> pitch-sensitive DTW geometry
            -> timing cross-talk
            -> timing non-monotonicity

local timing boundary movement
    |
    +--> frame/window content changes near transition
    |       -> pre-alignment pitch error
    |
    +--> DTW partially compensates
            -> smaller residual pitch cross-talk
```

## Recommended next machine-side experiment

Before R0.6 admits an event/perceptual primitive layer, test the narrower alignment hypothesis:

> Can an alignment substrate that does not depend strongly on pitch preserve useful correspondence while removing pitch -> timing cross-talk and improving timing monotonicity?

A suitable next experiment is an **Alignment Substrate Ablation v1** comparing the current DTW feature cost against controlled counterfactual cost families, without changing production behavior.

Candidate diagnostic variants:

- current pitch + energy + ZCR + voiced cost;
- pitch-free energy + ZCR structural cost;
- reduced-pitch cost;
- positional regularization added to the current cost.

The experiment should compare:

- pitch-drift timing cross-talk;
- local-timing monotonicity;
- alignment coverage/cost geometry;
- preservation of pitch target sensitivity.

Only if alignment ablations fail should R0.6 treat this particular timing defect as evidence for a deeper representation change.

## Human evidence boundary

R0.5b remains open as a separate evidence track.

No result in R0.5c substitutes for real within-session repeatability.

In particular, the remaining 0.764-point timing-warp -> pitch cross-talk and 0.013-point pitch-drift -> rhythm movement should not be assigned practical importance until compared with real human/session spread.
