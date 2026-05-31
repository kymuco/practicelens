# PracticeLens Roadmap

This roadmap describes the public product and engineering direction for PracticeLens.

It separates current capabilities, near-term execution, and long-term north-star work. It is a direction of travel, not a promise that every future capability will ship in this exact order.

## North star

PracticeLens should grow from a private practice-review tool into a local-first music practice intelligence platform.

The core loop is:

```text
record several takes -> compare against a reference -> find the strongest take -> understand the recurring weakness -> practice the next target -> compare progress later
```

PracticeLens should stay private by default, useful on real practice recordings, honest about confidence and limitations, and extensible toward instrument-aware, polyphonic, effect-aware, and ML/DL-assisted review.

## Product position

Current position:

> PracticeLens is a private practice-review tool for musicians who can already attempt a phrase, riff, or take and want objective feedback before asking other people.

It is currently strongest for short clean monophonic or near-monophonic reference-based review. Polyphony, chords, heavy effects, beginner tutoring, and full transcription are future directions, not current promises.

See also:

- `docs/product_positioning.md`
- `docs/known_limitations.md`
- `docs/real_audio_usage.md`

## Current baseline

Already in place:

- offline single-take analysis;
- multi-take batch comparison;
- JSON / Markdown / CSV / SVG outputs;
- practice-session workflow;
- `session_manifest.json`;
- JSONL session history index;
- `sessions list` / `sessions show` / `sessions compare` CLI surfaces;
- generated evaluation showcase;
- real-audio usage documentation;
- input suitability summary;
- duration mismatch diagnostics;
- start/leading-noise diagnostics;
- low-confidence Markdown warnings;
- real-audio smoke workflow documentation;
- manual real-audio trust checklist;
- optional API workflows for `/health`, `/analyze`, `/compare-batch`, and `/practice-session`;
- typed API payload contracts;
- CI and contributor-facing repo hygiene.

## Current execution focus

The current active milestone is:

```text
M2 — Practice Review UX v2
```

The goal is to answer the next product question:

> After a real practice session, does the user clearly understand what to keep, what to fix, and what to record next?

M2 should improve musician-facing review clarity without changing core scoring, alignment, or preprocessing behavior.

## Completed milestones

### M0 — Current Foundation

Goal: establish a working local-first practice-review baseline.

Status: complete.

Delivered capabilities:

- single-take analysis;
- batch comparison;
- practice-session workflow;
- session manifests;
- opt-in local history index;
- `sessions list/show/compare`;
- generated showcase;
- optional API surface;
- artifact documentation and tests.

### M1 — Real Audio Readiness

Goal: make PracticeLens honest and safer to try on real musician recordings, not only synthetic demo data.

Status: complete.

Delivered capabilities:

- real-audio usage guide;
- input suitability summary;
- duration mismatch diagnostic;
- leading silence / start offset diagnostic;
- low-confidence warnings in Markdown;
- real-audio smoke workflow docs;
- real-audio manual checklist.

## Near-term milestones

### M2 — Practice Review UX v2

Goal: make feedback more useful as practice guidance, not just report text.

Expected work:

- rewrite `practice_plan.md` around action;
- add `Before next take` section;
- explain why a recurring weakness matters;
- add per-take `Keep / Fix / Retry` summaries;
- clarify that the best take is only best among submitted takes;
- add Markdown snapshot tests for UX sections.

### M3 — Progress Tracking v2

Goal: make repeated sessions useful over time.

Possible future work:

- add a progress summary model;
- improve `sessions compare` output;
- add progress Markdown rendering;
- add `sessions compare --out`;
- add a simple `sessions trend` command;
- add progress contract tests.

### M4 — Instrument Profiles v1

Goal: stop treating every source as the same instrument.

Possible future work:

- add `instrument_profile` config;
- support `guitar_clean`, `vocal`, `bass`, `keyboard`, and `generic` profiles;
- add profile-specific feedback wording;
- add profile-specific suitability warnings;
- document supported profiles;
- test profile selection through CLI/API/reports.

## Capability milestones

### M5 — Music Event Layer v1

Goal: move from frame-only analysis toward musical events.

Possible future work:

- add `MusicEvent` model;
- extract event-like attacks/rests/sustains from existing DSP features;
- write `events.json` artifact;
- summarize events in Markdown;
- prototype event alignment;
- use events for missing-first-note diagnostics.

### M6 — Pluggable Analysis Backends

Goal: prepare the architecture for ML/DL without replacing the deterministic baseline.

Possible future work:

- define `FeatureExtractor` interface;
- define `AlignmentEngine` interface;
- define `ScoringEngine` interface;
- add backend registry/config;
- add backend metadata to reports;
- prove default output remains unchanged.

### M7 — ML-Assisted Monophonic Review

Goal: improve single-line pitch/onset/timing review through optional local ML backends.

Possible future work:

- add optional ML backend contract;
- add `practicelens doctor --ml`;
- add explicit unavailable-backend behavior;
- document local-first ML backend policy;
- add one real optional pitch backend;
- add DSP-vs-ML comparison artifacts.

### M8 — Chords / Polyphony v1

Goal: support first-pass harmonic/chord review without pretending to solve full transcription.

Possible future work:

- add `analysis_mode = monophonic | polyphonic_v1`;
- add chroma/pitch-class features;
- add `harmonic_match` metric;
- add chord-friendly report wording;
- add synthetic chord fixtures;
- add polyphonic batch tests;
- document what `polyphonic_v1` can and cannot judge.

### M9 — Note / Chord Event Representation v2

Goal: create a stronger event timeline for future transcription-aware review.

Possible future work:

- add `NoteEvent` model;
- add `ChordEvent` model;
- write `music_timeline.json`;
- add timeline Markdown summary;
- add timeline alignment;
- test event-level comparison on generated fixtures.

### M10 — Effect-Aware Recording Profiles

Goal: handle guitar recording realities such as distortion, delay, reverb, and compression with explicit caveats.

Possible future work:

- add `recording_profile` config;
- add effect suitability warnings;
- add noise/spectral diagnostics;
- document recording profiles;
- add `Recording caveats` report section;
- test warnings with generated noisy/effected fixtures.

## Product and ecosystem milestones

### M11 — Product Surface v1

Goal: make PracticeLens easier to use as a local product, not only as a library/CLI.

Possible future work:

- add `practicelens init`;
- load local project config;
- add simpler CLI aliases if they do not break existing commands;
- add local HTML report export;
- add `practicelens open` helper;
- add install/quickstart docs.

### M12 — HDE Skill Signal Export

Goal: let PracticeLens act as a focused music-practice signal source for a broader local-first personal development environment.

Possible future work:

- define an HDE skill signal contract;
- write `hde_skill_signal.json`;
- add `--export-skill-signal`;
- add skill signal pointers to `session_manifest.json`;
- document PracticeLens' role as a focused music-practice module;
- add contract tests.

This should remain a high-level export boundary. PracticeLens should own music-practice analysis; external systems should consume summarized practice signals, not raw private audio by default.

### M13 — Tutor Mode v0

Goal: cautiously support less confident users without pretending to be a full teacher.

Possible future work:

- document tutor mode boundaries;
- add practice breakdown renderer;
- add beginner-friendly feedback wording;
- add slow-practice recommendations;
- test tutor-mode Markdown.

### M14 — Advanced ML/DL Practice Intelligence

Goal: establish the evaluation and backend contracts needed before larger learned review models.

Possible future work:

- document dataset/evaluation protocol;
- define local evaluation dataset format;
- add evaluator runner;
- add model backend benchmark contract;
- add learned reviewer interface;
- document local-first model policy.

### M15 — Full Music Practice Platform

Goal: long-term product direction.

Possible future capabilities:

- multi-instrument sessions;
- backing-track-aware mode;
- arrangement-aware comparison;
- personal progress model;
- HDE companion handoff;
- packaged desktop/local app.

## Execution rule

Do not create issues for the whole north-star roadmap at once.

Use GitHub issues for the next executable milestone only, plus maybe one planning issue for the next milestone. Keep future milestones in this document until their prerequisites are real.

Current recommended GitHub issue focus:

```text
M2 — Practice Review UX v2
```

## Explicitly not immediate

The project should not immediately prioritize:

- cloud-first infrastructure;
- social features;
- beginner tutor mode;
- full transcription;
- polyphonic-first redesign;
- large model dependency by default;
- deep HDE integration before product-level music practice usefulness is stronger.

## Practical north star

PracticeLens should become:

- private by default;
- local-first;
- useful on real practice recordings;
- honest about confidence and limitations;
- clear about what to practice next;
- useful for tracking repeated sessions;
- extensible toward instrument-aware, polyphonic, effect-aware, and ML/DL-assisted review;
- eventually able to emit meaningful high-level music-practice signals for broader personal-development systems.
