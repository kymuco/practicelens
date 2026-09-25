# Recording-Start Equivalence Repair v1 — Results

Status: accepted / R0.5a follow-up complete

Scientific revision:

`a771a8d8e69740ba95f628cc5fe28eb5947c512f`

The final admitted candidate is **Candidate D — material DC centering plus exact activity trim**.

## Admission result

The unchanged R0.5a equivalence experiment now reports:

```text
tested equivalence floor

pitch_fidelity       0.000000
rhythm_fidelity      0.000000
timing_consistency   0.000000
section_stability    0.000000
```

Every admitted equivalence family is exactly invariant under the deterministic protocol:

```text
exact_copy       0 / 0 / 0 / 0
pcm_roundtrip    0 / 0 / 0 / 0
polarity         0 / 0 / 0 / 0
gain             0 / 0 / 0 / 0
dc_offset        0 / 0 / 0 / 0
recording_window 0 / 0 / 0 / 0
```

The original R0.5a baseline remains preserved separately and showed:

```text
pitch_fidelity       2.016078
rhythm_fidelity      1.419644
timing_consistency   7.009045
section_stability    3.837666
```

The demonstrated recording-window equivalence defect is therefore closed for the tested synthetic class.

## R0.4 preservation gate

The frozen R0.4 audit was rerun on the same scientific revision.

Family verdicts:

```text
amplitude_gain                PASS
deterministic_additive_noise  FAIL
local_timing_warp             PARTIAL
pitch_drift                   PARTIAL
```

This preserves the same qualitative validity structure as the pre-repair baseline.

### Amplitude gain

All four candidate measurements are exactly invariant again:

```text
pitch_fidelity       max delta 0
rhythm_fidelity      max delta 0
timing_consistency   max delta 0
section_stability    max delta 0
```

### Pitch drift

The primary signal remains strong:

```text
pitch_fidelity max |delta| = 25.348476
directional sensitivity   = PASS
monotonicity              = PASS
```

Strict protected specificity remains unresolved as a validated property:

```text
rhythm_fidelity max |delta|    = 0.013356
timing_consistency max |delta| = 2.275722
strict protected specificity  = FAIL
```

### Local timing warp

The timing signal remains present:

```text
timing_consistency max |delta| = 4.490712
directional sensitivity       = PASS
monotonicity                  = PARTIAL
```

Protected pitch still moves:

```text
pitch_fidelity max |delta| = 0.763684
strict protected specificity = FAIL
```

### Additive noise

The nuisance family remains a real unresolved boundary rather than being hidden by the repair:

```text
pitch_fidelity max |delta|       = 3.560936
rhythm_fidelity max |delta|      = 1.184859
timing_consistency max |delta|   = 4.509643
section_stability max |delta|    = 3.273450
strict nuisance invariance       = FAIL
```

## Candidate elimination history

The repair sequence materially narrowed the architecture:

1. **Candidate A — fixed zero padding:** rejected because it amplified DC-offset sensitivity.
2. **Candidate B1 — unconditional DC centering:** rejected because it introduced gain sensitivity.
3. **Candidate B2 — deadbanded DC centering + zero-only edge padding:** rejected because gain sensitivity remained.
4. **Candidate C — fixed 64-sample source context:** rejected because `amplitude_gain__12` still moved `rhythm_fidelity`.
5. **Candidate D — deadbanded material DC centering + exact activity trim:** admitted.

A diagnostic comparison also showed a 9-sample context could pass the tested gain/leading-silence cases, but that value was specific to the synthetic phrase and was rejected as an unjustified tuned parameter.

## Final preprocessing boundary

```text
resample if needed
  -> remove material DC acquisition bias when |mean| > 1e-4
  -> peak normalize
  -> trim exactly to |sample| >= 0.01 activity
  -> feature extraction
```

No score formula, feature extractor, alignment algorithm, or confidence/suitability rule was changed.

## Evidence

- `docs/synthetic_equivalence_baseline_v1.json` — immutable pre-repair R0.5a baseline;
- `docs/synthetic_equivalence_post_repair_v1.json` — admitted post-repair R0.5a result;
- `docs/measurement_validity_baseline_v1.json` — immutable pre-repair R0.4 baseline;
- `docs/measurement_validity_post_repair_v1.json` — post-repair R0.4 preservation gate.

## Next boundary

R0.5a now establishes zero deterministic movement across the tested synthetic equivalence class.

It still does **not** establish human repeatability.

The next experiment is R0.5b — Local Session Repeatability v1:

> estimate how much the candidate measurements move across repeated real takes when no skill-development interval is intended.

That human/session floor must be measured before longitudinal score changes are interpreted as development.
