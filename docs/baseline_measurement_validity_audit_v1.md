# Baseline Measurement Validity Audit v1

Status: R0.4

## Purpose

R0.4 freezes the current PracticeLens analysis instrument and runs it unchanged across the R0.3 controlled perturbation harness.

The audit asks four narrow questions:

1. Does the intended target measurement move in the expected score direction?
2. Is that response monotonic across ordered perturbation strengths?
3. Do explicitly protected measurements remain unchanged under the target intervention?
4. Do current component scores remain strictly invariant under nuisance-only interventions?

R0.4 does not tune the instrument in response to the results.

## Frozen instrument

The audit uses the existing `OfflineReferenceAnalysisPipeline` and current scoring implementation without modification.

The exact analysis configuration is:

```text
target_sample_rate = 16000
frame_length       = 1024
hop_length         = 256
segment_duration_s = 1.0

pitch_weight       = 0.35
rhythm_weight      = 0.30
timing_weight      = 0.20
stability_weight   = 0.15
```

The audited candidate measurements are:

- `pitch_fidelity`;
- `rhythm_fidelity`;
- `timing_consistency`;
- `section_stability`.

Each condition also records confidence level, input-suitability status, and alignment coverage as supporting diagnostics.

## Measurement records

Every R0.3 condition produces one R0.2 `MeasurementExperimentRecord`.

The record includes:

- intervention identity and strength;
- exact analysis configuration;
- generator provenance;
- optional exact code revision;
- the four candidate component-score values.

The record does not contain an expected answer.

## Target-family preregistration

### pitch_drift

Primary candidate measurement:

```text
pitch_fidelity
```

Protected measurements for strict specificity screening:

```text
rhythm_fidelity
timing_consistency
```

`section_stability` is not protected because it is a derived aggregate over section-level component behavior and therefore is not structurally independent.

### local_timing_warp

Primary candidate measurement:

```text
timing_consistency
```

Protected measurement:

```text
pitch_fidelity
```

`rhythm_fidelity` is not protected because the intervention deliberately changes an internal musical-event boundary and onset-oriented rhythm evidence may legitimately respond.

## Strict screening semantics

R0.4 intentionally uses an extremely strict deterministic epsilon:

```text
1e-9 score points
```

This is not a claim that a musician-facing measurement must be invariant to 1e-9 in practice.

It means:

> under a deterministic synthetic controlled experiment, did the current implementation produce exactly stable behavior up to floating-point tolerance?

R0.5 will later establish practical repeatability and the empirical noise floor needed for meaningful real longitudinal thresholds.

### Directional sensitivity

For a target family, the endpoint score of the primary candidate measurement must be lower than the family control because every current component score is oriented as higher-is-better.

- lower endpoint: `PASS`;
- higher endpoint: `FAIL`;
- unchanged endpoint: `UNRESOLVED`.

The magnitude is always reported separately.

### Monotonicity

For the primary candidate measurement:

- no increases and at least one decrease: `PASS`;
- some reversals but final score below control: `PARTIAL`;
- no change at all: `UNRESOLVED`;
- otherwise: `FAIL`.

### Strict protected specificity

Every protected candidate measurement must remain unchanged within the strict epsilon.

Any movement is a strict-screening `FAIL`, with the actual maximum absolute delta retained in the artifact.

### Strict nuisance invariance

Every audited component measurement is checked independently against its family-local zero control.

Again, any movement larger than the strict epsilon is a strict-screening `FAIL`.

This is intentionally stronger than the later practical interpretation.

## Family verdict

For nuisance families:

- all four strict invariance checks pass -> `PASS`;
- otherwise -> `FAIL`.

For target families:

- no directional response -> `UNRESOLVED`;
- wrong endpoint direction -> `FAIL`;
- correct sensitivity + monotonicity + protected specificity -> `PASS`;
- correct endpoint sensitivity with another strict property failing -> `PARTIAL`.

No overall "PracticeLens is valid/invalid" verdict is emitted.

The family-level results are evidence for the next architecture decision, not a universal certification.

## Outputs

The audit writes:

```text
out/measurement_validity_audit_v1/
  harness/
    manifest.json
    reference.wav
    cases/...
  records/
    <condition-id>.json
  summary.json
```

The executable entry point is:

```bash
python tools/run_measurement_validity_audit.py
```

## Interpretation boundary

A failed strict specificity check does not automatically mean a measurement is useless.

It can mean:

- the current feature extractor couples two physical variables;
- the score construction couples dimensions;
- the perturbation changes more observable structure than its high-level name suggests;
- or the candidate labels imply cleaner construct separation than the implementation actually provides.

R0.4 records that fact. It does not repair it.

## Next step

R0.5 should establish repeatability and a practical noise floor before small nonzero deltas are interpreted as meaningful human-development change.

The most important R0.4 output is therefore not the number of PASS verdicts. It is the exact pattern of response and cross-talk across controlled families.
