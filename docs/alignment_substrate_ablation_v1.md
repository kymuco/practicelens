# R0.5d — Alignment Substrate Ablation v1

Status: active experiment

## Trigger

R0.5c localized two important timing findings to DTW path geometry:

```text
pitch drift -> timing_consistency
    alignment_path

local timing monotonicity failure
    non-monotonic DTW path geometry
```

This means the narrowest machine-side question is now alignment, not representation.

R0.5d asks:

> Can a preregistered alignment substrate reduce pitch-induced timing cross-talk and restore monotonic timing response while preserving useful pitch sensitivity?

Production alignment remains unchanged.

## Frozen controlled targets

The experiment reuses the existing R0.3 families:

- `pitch_drift`: 0 / 0.01 / 0.03 / 0.06;
- `local_timing_warp`: 0 / 20 / 40 / 80 ms.

No new perturbation is added.

## Profiles

R0.5d preregisters five coarse profiles.

The point is not to optimize weights.

The point is to ask which alignment ingredients are causally responsible.

### current

Exact production cost:

```text
pitch  0.55
energy 0.25
ZCR    0.20
voiced mismatch penalty 0.40
position penalty 0
```

The diagnostic implementation must reproduce production DTW exactly.

### pitch_half

Halve explicit pitch dependence and the voiced-mismatch penalty.

The removed feature weight is redistributed to energy and ZCR in their existing 5:4 ratio:

```text
pitch  0.275
energy 0.402777...
ZCR    0.322222...
voiced mismatch penalty 0.20
position penalty 0
```

### pitch_free_structural

Remove pitch and voiced state from alignment:

```text
pitch  0
energy 5/9
ZCR    4/9
voiced mismatch penalty 0
position penalty 0
```

This tests whether energy/ZCR structure alone can preserve useful temporal correspondence.

### current_positional_0p10

Keep the current feature cost and add:

```text
0.10 * |normalized reference position - normalized take position|
```

This asks whether a weak diagonal prior can suppress pitch-driven path wandering without removing pitch from the cost.

### pitch_half_positional_0p10

Combine the two bounded interventions:

- half pitch dependence;
- 0.10 positional regularization.

No additional profiles are added after observing results.

## Measurements

### Pitch-drift target

For each profile record:

- `pitch_fidelity` sequence;
- pitch directional sensitivity;
- pitch monotonicity;
- `timing_consistency` sequence;
- maximum pitch -> timing cross-talk.

### Local-timing target

For each profile record:

- `timing_consistency` sequence;
- timing directional sensitivity;
- timing monotonicity;
- endpoint timing delta;
- `pitch_fidelity` sequence;
- maximum timing -> pitch cross-talk.

### Path geometry

Across all target conditions:

- minimum coverage;
- maximum mean normalized position error;
- maximum warp-step fraction.

## Strict narrow hypothesis

A non-current profile meets the preregistered narrow hypothesis only if all of the following hold:

1. pitch-drift timing cross-talk is **strictly lower** than current;
2. local-timing directional sensitivity is `PASS`;
3. local-timing monotonicity is `PASS`;
4. pitch-drift directional sensitivity is `PASS`;
5. pitch-drift monotonicity is `PASS`;
6. minimum alignment coverage is not lower than current.

There is deliberately no post-hoc score-improvement threshold.

A tiny nonzero timing response can satisfy directional sensitivity, so response magnitude is always reported and must be considered before any production admission.

## Interpretation

### If no profile meets the narrow hypothesis

The current defect is not eliminated by these coarse alignment-space ablations.

That strengthens the case for either:

- a more explicit event/transition alignment substrate;
- or a deeper representation change.

It does not automatically admit one.

### If one or more profiles meet it

Then at least the main timing defect is demonstrably solvable inside alignment-space.

R0.6 should not cite that defect as evidence for replacing the frame-level representation.

A separate validation step would still be required before changing production DTW.

## Non-goals

R0.5d does not:

- select a production winner;
- tune profile weights;
- alter current DTW;
- alter scoring;
- solve additive-noise nuisance;
- replace R0.5b human/session evidence.
