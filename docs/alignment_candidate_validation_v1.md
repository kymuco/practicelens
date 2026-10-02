# R0.5e — Alignment Candidate Validation v1

Status: complete / broader synthetic validation recorded

## Trigger

R0.5d showed that the preregistered profile:

```text
current_positional_0p10
```

solves the narrow timing-path defect:

- pitch-drift -> timing cross-talk decreases;
- local-timing response becomes monotonic;
- pitch target sensitivity remains present;
- alignment coverage remains complete.

It also showed trade-offs:

- local-timing response magnitude is compressed;
- timing-warp -> pitch residual increases.

R0.5e therefore asks a broader question:

> Does the frozen positional candidate remain acceptable across all existing synthetic target and nuisance evidence without tuning its weight?

Production DTW remains unchanged.

## Frozen candidate

The candidate is imported directly from R0.5d:

```text
pitch weight              0.55
energy weight             0.25
ZCR weight                0.20
voiced mismatch penalty   0.40
position penalty          0.10
```

No new candidate and no new weight are added in R0.5e.

## Families

The validation reruns every current R0.3 family:

- `amplitude_gain`;
- `deterministic_additive_noise`;
- `pitch_drift`;
- `local_timing_warp`.

For every condition it records production scores and candidate scores side by side.

## Preregistered synthetic checks

### amplitude gain

The candidate must preserve strict invariance across all four candidate measurements.

### additive noise

Because production already fails strict additive-noise invariance, R0.5e does not require the candidate to solve it.

Instead it requires a strict no-regression property:

> no candidate measurement may have a larger maximum absolute noise delta than production.

This prevents the timing repair from quietly worsening an unrelated nuisance boundary.

### pitch drift

The candidate must preserve:

- directional pitch sensitivity;
- monotonic pitch response;
- protected cross-talk no worse than production for rhythm and timing.

Response magnitudes are recorded.

### local timing warp

The candidate must preserve:

- directional timing sensitivity;
- monotonicity must be `PASS`;
- protected pitch cross-talk must be no worse than production.

The last requirement is deliberately strict. R0.5d already suggested that the positional prior may fail it.

R0.5e records that as a real trade-off rather than weakening the criterion after seeing the result.

### coverage

Minimum candidate alignment coverage must not be lower than production for any family.

## Why response magnitude is not a hard gate

R0.5d showed that the positional prior compresses the local-timing endpoint response.

R0.5e reports the exact retention ratio but does not invent a threshold such as 50% or 80%.

The reason is scientific rather than permissive:

```text
deterministic equivalence floor = 0
human/session repeatability      = not measured yet
```

Without R0.5b, there is no evidence-backed minimum useful score movement.

The magnitude trade-off therefore remains explicit evidence, not a synthetic PASS/FAIL threshold.

## Outcome semantics

`passes_all_preregistered_checks = true` means only that the candidate survived this broader synthetic validation screen.

It does not admit production behavior.

A failed check is equally useful: it identifies the exact boundary that blocks candidate admission.

## Recorded result

Canonical evidence:

- `docs/alignment_candidate_validation_baseline_v1.json`;
- `docs/alignment_candidate_validation_results_v1.md`.

The frozen candidate does **not** pass all preregistered checks.

Passed:

- amplitude-gain strict invariance;
- pitch-drift sensitivity and monotonicity;
- pitch-drift protected cross-talk no worse;
- local-timing sensitivity;
- local-timing monotonicity improved to PASS;
- alignment coverage preserved.

Failed:

- additive-noise per-measurement no-regression;
- local-timing protected pitch cross-talk no worse.

The candidate therefore remains diagnostic rather than production-admissible.

## Non-goals

R0.5e does not:

- tune positional weight;
- search more profiles;
- modify production DTW;
- claim human significance;
- solve additive-noise nuisance;
- replace R0.5b.
