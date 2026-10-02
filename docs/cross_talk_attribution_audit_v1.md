# R0.5c — Cross-Talk Attribution Audit v1

Status: complete / attribution baseline recorded

## Trigger

R0.4 established three protected-dimension movements that remain after the R0.5a recording-origin repair:

```text
pitch drift
  -> rhythm_fidelity moves slightly
  -> timing_consistency moves

local timing warp
  -> pitch_fidelity moves
```

R0.5a shows the tested deterministic equivalence floor is now zero.

R0.5c asks a narrower architecture question:

> At what stage does each protected-dimension movement first appear?

## Pipeline boundaries

The current path is:

```text
audio
  -> preprocessing
  -> feature extraction
  -> DTW alignment
  -> score construction
```

R0.5c does not modify any of those stages.

It observes them.

## Score dependency map

The current score functions already impose useful causal constraints.

### pitch_fidelity

Consumes:

```text
pitch_contour_hz
voiced_mask
DTW alignment pairs
```

It does not consume rhythm or timing scores.

### rhythm_fidelity

Consumes:

```text
onset_times_s
time_axis_s
```

It does **not** consume DTW alignment.

Therefore pitch-drift -> rhythm movement cannot be caused by DTW or by another component score feeding the rhythm score. If it exists, it must already be present in the onset/time representation used by the scorer.

### timing_consistency

Consumes:

```text
frame_count
DTW alignment path geometry
```

It does not directly consume pitch values.

Therefore pitch-drift -> timing movement can only arise because pitch affects the alignment path, or because frame-count/preprocessing changes.

## Linear-alignment counterfactual

For every controlled target condition R0.5c computes two score sets.

### Observed

```text
features
  -> current feature-similarity DTW
  -> current scorer
```

### Counterfactual linear alignment

```text
same exact extracted features
  -> monotonic relative-position mapping
  -> same current scorer
```

The linear mapping ignores pitch, energy, ZCR, and voiced similarity.

This is not a proposed production alignment algorithm.

It is an attribution intervention.

If protected movement exists under both observed and linear alignments, the movement is already present before the observed DTW path is applied.

If movement is absent under linear alignment but appears with observed DTW, the alignment path is the source.

If both components are nonzero, attribution is mixed.

## Pre-alignment diagnostics

R0.5c also records:

- frame-count delta;
- voiced-ratio delta;
- onset-count delta;
- tempo delta;
- relative-position pitch cents error;
- voiced mismatch fraction;
- energy delta;
- ZCR delta;
- normalized onset nearest-distance.

These are evidence for deciding whether a pre-alignment score change corresponds to a changed feature representation rather than an opaque scorer interaction.

## Alignment diagnostics

For the observed DTW path:

- pair count;
- coverage;
- total and mean local cost;
- mean/max normalized position error;
- horizontal/vertical warp-step fraction.

The timing score is directly related to normalized position error, so this exposes its mechanism rather than only its final 0-100 value.

## Attribution vocabulary

```text
none
alignment_path
pre_alignment_feature_or_score_path
mixed_pre_alignment_and_alignment
unresolved
```

R0.5c deliberately uses `pre_alignment_feature_or_score_path` rather than overclaiming that every pre-DTW effect has already been separated into extraction vs scoring.

The feature diagnostics provide the evidence needed for the next narrowing step if that distinction matters.

## Scope

The first audit covers only the target families already used for R0.4 specificity:

- `pitch_drift`;
- `local_timing_warp`.

It does not add new perturbations.

It does not repair the discovered cross-talk.

## Decision value

Useful possible outcomes include:

### pitch -> timing is alignment-only

Then a new perceptual/event representation is not yet justified for that defect. The narrower issue is alignment cost/path ownership.

### timing -> pitch exists before alignment

Then frame-level pitch representation around event boundaries is a stronger suspect, and an event/transition representation becomes a more specific R0.6 candidate.

### pitch -> rhythm exists in onset features

Then the onset extractor has a cross-domain sensitivity that should be addressed separately from DTW.

This is why R0.5c comes before a broad representation rewrite.

## Recorded result

Canonical evidence:

- `docs/cross_talk_attribution_baseline_v1.json`;
- `docs/cross_talk_attribution_results_v1.md`.

Recorded attribution:

```text
pitch drift -> rhythm_fidelity
    pre-alignment onset/time path

pitch drift -> timing_consistency
    alignment_path

local timing warp -> pitch_fidelity
    mixed pre-alignment + alignment
    with the dominant pre-alignment effect reduced by DTW
```

The local-timing monotonicity failure is also localized to DTW path geometry rather than the final timing score mapping.
