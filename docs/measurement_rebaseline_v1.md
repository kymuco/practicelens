# PracticeLens Measurement Rebaseline v1

Status: R0.1 design baseline  
Date: 2026-09-24

## Decision

PracticeLens is being rebaselined from a product-first practice-review roadmap toward a research-first role:

> PracticeLens is a local-first observation and measurement system for musical skill development.

The existing practice-review product remains useful. This rebaseline does not remove the CLI, API, reports, session history, or current deterministic analysis pipeline. It changes what future work must prove before the project expands.

The long-term research goal is to make PracticeLens the first serious laboratory-grade domain sensor for human development: a bounded music-specific system that converts repeated practice activity into compact, evidence-backed observations about change over time.

"Laboratory-grade" is a target, not a current claim.

## Why rebaseline now

The current system already has a coherent end-to-end loop:

```text
audio
  -> preprocessing
  -> deterministic features
  -> reference-aware alignment
  -> component scores
  -> reports / practice guidance
  -> session history
```

It also has deterministic synthetic evaluation cases for pitch drift, timing drift, rhythm mistakes, noise, silence mismatch, vibrato, pluck-like envelopes, and tempo mismatch.

That is enough infrastructure to ask a more important question than "what feature should we add next?":

> Does the current instrument measure the constructs that its labels imply?

The existing evaluation showcase is useful for demos and smoke checks, but it explicitly is not a scientific benchmark. The next phase therefore validates the measurement instrument before adding ML, polyphony, tutoring, or broader product surfaces.

## Object of measurement

PracticeLens does not directly observe "skill".

It observes audio and derives bounded evidence from it.

The intended chain is:

```text
raw observation
    -> derived acoustic / temporal evidence
    -> candidate measurement
    -> repeated-trial evidence
    -> cautious skill-development inference
```

Each transition must remain inspectable.

A future claim about human development must be traceable back to observations and must carry enough uncertainty and provenance to show how strongly the evidence supports it.

## Claim levels

PracticeLens distinguishes four levels of statement.

### Level 0 — observed

Directly obtained from the recording or deterministic preprocessing.

Examples:

- duration;
- sample rate;
- detected activity region;
- detected onset time;
- estimated pitch track;
- voiced-frame coverage.

### Level 1 — derived

Computed from observed evidence under an explicit transformation.

Examples:

- aligned onset offset;
- pitch deviation after alignment;
- duration ratio;
- alignment coverage;
- within-take timing variance.

### Level 2 — inferred

An interpretation supported by repeated or aggregated derived evidence.

Examples:

- repeated late-onset tendency;
- timing variability decreased across comparable sessions;
- a failure appears above a particular tempo condition.

These claims require provenance, comparison conditions, and uncertainty.

### Level 3 — unsupported without additional evidence

PracticeLens must not silently jump from signal evidence to causal or pedagogical diagnosis.

Examples:

- "bad technique";
- "poor rhythm ability";
- "you do not understand the phrase";
- "this fingering is wrong";
- "you are tired";
- "your skill improved" when the observed change is not distinguishable from execution, recording, or measurement variability.

Such claims require evidence that the current audio-only instrument does not necessarily possess.

## Candidate measurements

The current score dimensions are retained, but their labels must be treated as candidate measurements until experimentally validated:

- `pitch_fidelity`;
- `rhythm_fidelity`;
- `timing_consistency`;
- `section_stability`;
- overall score and rankings derived from them.

R0 does not assume that these dimensions have construct validity merely because their outputs look plausible.

A candidate measurement may be retained, narrowed, renamed, decomposed, or rejected after validation.

## Nuisance variables

A laboratory-grade sensor must distinguish target variation from variation that should not be interpreted as skill change.

The first controlled nuisance set includes:

- overall amplitude / gain;
- short leading silence;
- short trailing silence;
- benign sample-rate representation changes;
- small broadband noise;
- recording envelope changes that preserve the target timing/pitch structure;
- small alignment-preserving offsets;
- codec or quantization changes if later introduced into the harness.

Additional nuisance variables may be added when real recordings expose them.

## Target interventions

The first controlled target set should vary one intended factor at a time:

- constant pitch offset;
- progressive pitch drift;
- isolated onset shift;
- progressive local timing warp;
- global tempo change;
- missing or strongly attenuated event;
- inserted pause;
- articulation/envelope change.

Interventions should be generated at multiple strengths, including a zero-change control.

## Measurement properties to test

### Sensitivity

A candidate measurement should change when its target construct is deliberately changed.

### Monotonic response

When an intervention grows stronger in an ordered synthetic series, the relevant measurement should generally respond in the expected direction unless a documented nonlinearity explains otherwise.

### Specificity

Changing one target factor should not collapse unrelated measurement dimensions without evidence that the constructs are actually coupled.

### Nuisance invariance

A change that is irrelevant to the claimed construct should not masquerade as change in that construct.

### Repeatability

Repeated equivalent observations should expose the instrument's own variability and the variability of the performance process.

### Uncertainty

Longitudinal claims should eventually distinguish observed change from execution stochasticity, recording variation, and measurement error.

### Provenance

Every higher-level claim must remain traceable to the observations, transformations, configuration, and comparison conditions that produced it.

## Laboratory-grade admission rule

PracticeLens may describe itself as pursuing laboratory-grade measurement now, but a specific measurement is not admitted as validated until it has evidence for the properties relevant to its use.

At minimum, a longitudinal skill-development measurement should have:

1. controlled sensitivity evidence;
2. nuisance robustness evidence;
3. specificity evidence;
4. repeatability / noise-floor evidence;
5. explicit failure boundaries;
6. provenance sufficient to reproduce the result.

Real-musician validation is still required after synthetic controlled validation. Synthetic PASS is necessary evidence for some claims, not final proof of ecological validity.

## Research sequence

### R0.1 — Measurement Rebaseline v1

This document.

Scope:

- redefine the scientific mission;
- define the observation -> measurement -> inference boundary;
- freeze current scores as candidate measurements;
- define the first nuisance and target intervention families;
- pause roadmap expansion that is not justified by measurement evidence.

No runtime behavior changes.

### R0.2 — Measurement Contract v1

Make the conceptual boundary executable and inspectable.

Expected work may include:

- explicit observation / derived-evidence terminology in evaluation code;
- provenance fields for controlled evaluation;
- stable experiment result schema;
- no change to scoring semantics.

### R0.3 — Controlled Perturbation Harness v1

Extend the current deterministic synthetic generator into parameterized intervention families.

Requirements:

- one factor varied at a time;
- ordered intervention strengths;
- deterministic fixtures;
- zero-change controls;
- machine-readable intervention metadata.

### R0.4 — Baseline Measurement Validity Audit v1

Run the current, unchanged measurement instrument against the controlled harness.

Primary outputs:

- sensitivity matrix;
- monotonicity results;
- specificity / cross-talk matrix;
- nuisance-invariance results;
- explicit PASS / PARTIAL / FAIL / UNRESOLVED verdicts per candidate measurement.

The audit must not modify scoring to make the audit pass.

### R0.5 — Repeatability and Noise Floor v1

Estimate how much apparent change exists when the intended underlying condition is unchanged or near-equivalent.

This phase establishes whether later longitudinal deltas are larger than the instrument/performance noise floor.

### R0.6 — Representation Admission Decision v1

Only after R0.4/R0.5 identify a concrete representational failure do we decide whether a new layer is justified.

Candidate directions include event/perceptual primitives such as:

- attack;
- sustain;
- transition;
- rest;
- event boundary.

The new representation is admitted only against a falsifiable hypothesis, for example:

> an event-level representation separates local timing/articulation changes from nuisance variation better than the current frame-level representation.

If the hypothesis fails, the representation is not kept merely because it is architecturally attractive.

## Relationship to ML

R0 introduces no learned model.

Future ML work must answer a demonstrated measurement deficiency. The preferred sequence is:

```text
define observable
  -> validate deterministic baseline
  -> identify failure boundary
  -> ask whether missing information is recoverable
  -> introduce the smallest model that improves the validated measurement
```

ML is an instrument component, not the scientific objective.

## Relationship to HDE and other domains

PracticeLens remains responsible for music-domain observation and measurement.

A broader system may later consume compact high-level evidence, but PracticeLens should not own general personal memory, motivation, identity, or cross-domain development reasoning.

The transferable result of this project is therefore not expected to be shared application code. It is the measurement architecture:

```text
domain activity
  -> bounded observations
  -> validated measurements
  -> uncertainty + provenance
  -> longitudinal evidence
  -> external development system
```

If this architecture works for music, other skill domains can adopt the same discipline with their own domain-specific sensors.

## Explicit non-goals for R0

R0 does not prioritize:

- new product UI;
- beginner tutor mode;
- full transcription;
- polyphonic-first redesign;
- large model integration;
- generic plugin/backend infrastructure;
- deep HDE integration;
- new scoring dimensions without a validation question;
- optimizing existing metrics before the baseline audit records their failures.

## Success condition

R0 succeeds even if several current PracticeLens measurements fail.

A useful failure that identifies exactly what the current representation cannot measure is more valuable than an impressive-looking score with unknown validity.

The output of R0 should be a smaller, better-justified space of future architectures.
