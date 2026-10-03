# PracticeLens Roadmap

This roadmap was rebaselined on 2026-09-24.

The previous product-first M2-M15 sequence is no longer treated as a linear execution plan. PracticeLens now follows a research-first rule: new capability is added only when the current measurement layer exposes a concrete, experimentally demonstrated limitation.

See [Measurement Rebaseline v1](measurement_rebaseline_v1.md).

## North star

PracticeLens should become a local-first, laboratory-grade domain sensor for musical skill development.

"Laboratory-grade" is a target, not a claim about the current implementation.

The desired long-term chain is:

```text
practice activity
  -> bounded music-domain observations
  -> validated measurements
  -> uncertainty + provenance
  -> longitudinal evidence
  -> optional external development systems
```

The project should remain useful as a private practice-review tool while becoming substantially stricter about what its scores are allowed to mean.

## Current baseline

Already in place:

- offline single-take analysis;
- multi-take batch comparison;
- deterministic feature extraction;
- reference-aware DTW alignment;
- pitch, rhythm, timing, and section-stability score dimensions;
- JSON / Markdown / CSV / SVG outputs;
- practice-session workflow;
- session manifests and opt-in local history;
- `sessions list/show/compare`;
- deterministic synthetic evaluation assets;
- generated evaluation showcase;
- input suitability and confidence warnings;
- real-audio usage and trust documentation;
- optional FastAPI surface;
- CI and contributor-facing repo hygiene.

Completed historical milestones:

- M0 — Current Foundation;
- M1 — Real Audio Readiness.

M2 — Practice Review UX v2 was partially completed through PR2.1 and PR2.2 before the research rebaseline. Remaining M2 issues are paused rather than assumed to be the next priority.

## Active research track — R0 Measurement Foundations

### R0.1 — Measurement Rebaseline v1

Status: complete.

Goal:

- define the scientific mission;
- separate observation, derivation, measurement, and inference;
- classify existing scores as candidate measurements;
- define nuisance variables and target interventions;
- establish the rule that future architecture must be justified by measurement evidence.

No scoring or runtime behavior changes.

### R0.2 — Measurement Contract v1

Status: complete.

Goal: make experiments reproducible and machine-readable.

Candidate work:

- controlled experiment metadata;
- provenance schema;
- explicit intervention identity and strength;
- explicit candidate-measurement outputs;
- stable audit artifact format.

No scoring changes.

### R0.3 — Controlled Perturbation Harness v1

Status: complete.

Goal: turn the current synthetic showcase foundation into a controlled measurement harness.

Delivered intervention families:

- `amplitude_gain` nuisance;
- `deterministic_additive_noise` nuisance;
- `pitch_drift` target;
- `local_timing_warp` target.

Each family contains a family-local zero control and ordered strengths. Additional intervention families remain evidence-driven extensions rather than assumed roadmap work.

### R0.4 — Baseline Measurement Validity Audit v1

Status: complete / baseline recorded.

Goal: evaluate the unchanged baseline.

For each candidate measurement, test:

- sensitivity;
- monotonic response;
- specificity;
- cross-talk;
- nuisance invariance;
- explicit failure boundaries.

Expected verdict vocabulary:

```text
PASS
PARTIAL
FAIL
UNRESOLVED
```

Do not repair metrics during the audit.

Recorded strict-screening result:

```text
amplitude_gain                PASS
deterministic_additive_noise  FAIL
local_timing_warp             PARTIAL
pitch_drift                   PARTIAL
```

See:

- `docs/measurement_validity_baseline_v1.json`;
- `docs/baseline_measurement_validity_results_v1.md`.

### R0.5 — Repeatability and Noise Floor v1

Status: active / machine-side synthetic work complete; human repeatability evidence pending.

Goal: determine how much variation exists without an intended underlying skill change.

This is required before longitudinal score differences can be interpreted as development evidence.

#### R0.5a — Synthetic Equivalence Floor v1

Status: complete / baseline recorded.

Results:

```text
exact rerun floor:
pitch_fidelity       0.000000
rhythm_fidelity      0.000000
timing_consistency   0.000000
section_stability    0.000000

tested equivalence envelope:
pitch_fidelity       2.016078
rhythm_fidelity      1.419644
timing_consistency   7.009045
section_stability    3.837666
```

The envelope is dominated by leading recording silence. A 16 ms or 64 ms leading pad produces the same downstream deltas, including a 7.01-point timing shift.

This is a systematic recording-window equivalence defect, not stochastic repeatability noise.

See:

- `docs/synthetic_equivalence_baseline_v1.json`;
- `docs/synthetic_equivalence_results_v1.md`.

#### R0.5a follow-up — Recording-Start Equivalence Repair v1

Status: complete / admitted.

The final repair uses:

```text
material DC centering (|mean| > 1e-4)
-> peak normalization
-> exact activity trim
```

Post-repair R0.5a result:

```text
pitch_fidelity       0.000000
rhythm_fidelity      0.000000
timing_consistency   0.000000
section_stability    0.000000
```

The unchanged R0.4 preservation audit restores `amplitude_gain = PASS` and preserves target sensitivity.

See:

- `docs/recording_start_equivalence_repair_results_v1.md`;
- `docs/synthetic_equivalence_post_repair_v1.json`;
- `docs/measurement_validity_post_repair_v1.json`.

#### R0.5b — Local Session Repeatability v1

Status: protocol/runner complete; first real session evidence pending.

Goal: estimate within-session variation from repeated real takes collected with no intended skill-development interval.

Private audio remains local; only compact measurement evidence should be exportable.

#### R0.5c — Cross-Talk Attribution Audit v1

Status: complete / baseline recorded.

Result:

```text
pitch drift -> rhythm
    pre-alignment onset/time micro-movement

pitch drift -> timing
    DTW alignment path

local timing warp -> pitch
    mixed, with frame-level boundary effect before DTW
    and DTW mostly compensating it
```

The previous timing-monotonicity failure is explained by non-monotonic DTW path geometry, not by the final timing score mapping.

See:

- `docs/cross_talk_attribution_baseline_v1.json`;
- `docs/cross_talk_attribution_results_v1.md`.

#### R0.5d — Alignment Substrate Ablation v1

Status: complete / baseline recorded.

Result:

```text
current_positional_0p10
pitch_half_positional_0p10
    -> meet strict narrow hypothesis

pitch_half
pitch_free_structural
    -> do not
```

The simplest successful diagnostic profile reduces pitch->timing cross-talk from 2.276 to 0.537 and restores monotonic local-timing response while preserving pitch sensitivity and full coverage.

Trade-offs remain:

- local-timing endpoint response is compressed from -4.389 to -1.610;
- timing->pitch residual rises from 0.764 to 1.022.

See:

- `docs/alignment_substrate_ablation_baseline_v1.json`;
- `docs/alignment_substrate_ablation_results_v1.md`.

#### R0.5e — Alignment Candidate Validation v1

Status: complete / broader synthetic validation recorded.

The frozen `current_positional_0p10` candidate does not pass all preregistered checks.

It preserves:

- amplitude-gain invariance;
- pitch-drift sensitivity and monotonicity;
- reduced pitch->timing cross-talk;
- monotonic local-timing response;
- full coverage.

It regresses:

- additive-noise pitch movement: 3.561 -> 3.770;
- local-timing protected pitch movement: 0.764 -> 1.022.

See:

- `docs/alignment_candidate_validation_baseline_v1.json`;
- `docs/alignment_candidate_validation_results_v1.md`.

No production DTW change is admitted.

#### R0.5f — Metric-Specific Alignment Readout Ablation v1

Status: complete / strict synthetic hypothesis supported.

Result:

```text
passes_all_preregistered_checks = true
```

Metric-specific ownership recovers the desired trade-off:

```text
pitch_fidelity
    -> production flexible alignment

timing_consistency
    -> current_positional_0p10 alignment

rhythm_fidelity
    -> unchanged onset/time path
```

Key effects:

- additive-noise pitch movement returns to production: 3.561;
- additive-noise timing movement drops: 4.510 -> 0.641;
- pitch-drift timing cross-talk drops: 2.276 -> 0.537;
- local-timing pitch cross-talk remains at production: 0.764;
- local-timing monotonicity becomes PASS;
- both alignment paths retain full coverage.

See:

- `docs/metric_specific_alignment_readout_baseline_v1.json`;
- `docs/metric_specific_alignment_readout_results_v1.md`.

This supports shared-alignment coupling, not frame-level insufficiency, as the current timing architecture defect.

#### R0.5g — Additive Noise Attribution Audit v1

Status: complete / baseline recorded.

Result:

```text
noise -> pitch_fidelity
    feature_extraction_with_alignment_contribution

noise -> rhythm_fidelity
    feature_extraction
```

Pitch evidence:

- relative-position pitch error rises to 7.599 cents at noise 0.06;
- voiced mismatch fraction remains 0;
- production DTW partially compensates the extractor error;
- production pitch movement is 3.561 points versus 3.799 under linear alignment.

Rhythm evidence:

- low-noise movement is tiny onset-position drift;
- at noise 0.06 the onset count changes 23 -> 24;
- the extra-onset count term contributes about 91.7% of the final 1.185-point rhythm movement.

Score reconstruction error is zero for the audited pitch/rhythm paths.

See:

- `docs/additive_noise_attribution_baseline_v1.json`;
- `docs/additive_noise_attribution_results_v1.md`.

The remaining noise failures are estimator-local rather than evidence that a new event representation is required.

### R0.6 — Representation Admission Decision v1

Status: complete / event-perceptual primitive layer not admitted.

Decision:

```text
CURRENT_FRAME_LEVEL_REPRESENTATION
    RETAIN

EVENT_PERCEPTUAL_PRIMITIVE_LAYER
    NOT_ADMITTED

REASON
    NO_DEMONSTRATED_REPRESENTATIONAL_GAP
```

The current machine-side failures have all been localized below the representation-admission boundary:

- recording-start equivalence -> preprocessing;
- pitch/timing coupling -> shared alignment ownership;
- additive-noise pitch movement -> pitch estimator robustness;
- additive-noise rhythm movement -> onset detector robustness;
- current score construction -> exactly reconstructable from observed feature terms.

R0.5f additionally shows that the tested timing conflict can be removed with construct-specific alignment readouts while retaining the same frame-level feature representation.

See:

- `docs/representation_admission_decision_v1.json`;
- `docs/representation_admission_decision_v1.md`.

The representation question should reopen only after a new controlled or real-session failure demonstrates an observable that cannot be recovered through preprocessing, estimator, alignment, or score boundaries.

## After the machine-side R0 decision

The synthetic machine-side architecture track is now complete enough to stop expanding by default.

R0 itself is **not ecologically complete** because R0.5b still lacks the first real-session repeatability sample.

After that evidence arrives, candidate directions include:

- real-musician repeatability validation;
- longitudinal development evidence;
- controlled tempo-condition experiments;
- event/perceptual primitive representation;
- instrument-specific measurement boundaries;
- small learned components for demonstrated observability gaps;
- high-level evidence export to HDE or another development system.

The R0 evidence determines their order.

## Paused legacy directions

The following ideas remain possible, but they are not active milestones merely because they appeared in the old roadmap:

- remaining Practice Review UX v2 work;
- Progress Tracking v2 product surfaces;
- instrument profiles;
- generic pluggable analysis backends;
- ML-assisted monophonic review;
- chords/polyphony;
- note/chord transcription representations;
- effect-aware profiles;
- larger standalone product surfaces;
- tutor mode;
- advanced learned reviewers;
- full music-practice platform expansion.

Any of these may return if a validated measurement need justifies them.

## Relationship to HDE

PracticeLens owns music-domain observation and measurement.

A broader development environment may consume summarized evidence later, but HDE integration is not a prerequisite for validating PracticeLens and should not distort the measurement model.

The first export boundary should eventually prefer compact evidence, uncertainty, conditions, and provenance over raw private audio.

## Execution rules

1. Do not add a new capability only because it is plausible or attractive.
2. Every research PR should state the hypothesis or measurement boundary it addresses.
3. Prefer experiments that eliminate architecture families over experiments that merely add options.
4. Freeze the instrument before a baseline audit; do not tune against the same audit used to claim validity.
5. Treat synthetic validation as controlled evidence, not proof of real-world ecological validity.
6. Record failures explicitly.
7. Introduce ML only after a concrete deterministic measurement deficiency is demonstrated.
8. Keep raw user recordings local by default.
9. Keep domain observation separate from general personal-development interpretation.

## Immediate next step

The machine-side representation decision is complete.

The next high-value evidence is:

```text
human evidence
    R0.5b — collect the first local-session repeatability sample when convenient
```

Until R0.5b exists, do not create another machine-side architecture milestone merely to maintain momentum.

A new machine-side experiment should require a newly demonstrated measurement failure.

R0.5b remains necessary before assigning practical human significance to residual score movements or making longitudinal development claims.
