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

Status: active.

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

Status: active next step.

Goal:

- repair the demonstrated leading-recording-silence sensitivity at the preprocessing/frame-origin boundary;
- re-run the frozen R0.5a equivalence experiment;
- require the repair to improve equivalence behavior without tuning against R0.4 target interventions.

Do not change score semantics in this repair.

#### R0.5b — Local Session Repeatability v1

Status: blocked on the R0.5a follow-up.

Goal: estimate within-session variation from repeated real takes collected with no intended skill-development interval.

Private audio remains local; only compact measurement evidence should be exportable.

### R0.6 — Representation Admission Decision v1

Goal: decide whether the existing frame-level representation is sufficient.

Possible next representation:

```text
Event
Attack
Sustain
Transition
Rest
```

An event/perceptual primitive layer is added only if it wins against a falsifiable hypothesis derived from R0.4/R0.5 failures.

## After R0

The next track is intentionally not frozen yet.

Candidate directions include:

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

The next executable task is:

```text
R0.5a follow-up — Recording-Start Equivalence Repair v1
```

R0.5a established exact deterministic repeatability but exposed a larger upstream nuisance: equivalent leading recording silence can move `timing_consistency` by 7.01 points, more than the 4.35-point maximum response to the R0.4 local timing target.

Repair and re-audit this boundary before collecting the R0.5b human/session repeatability baseline.
