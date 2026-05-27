# PracticeLens Roadmap

This roadmap separates the north-star direction from the immediate execution plan.

PracticeLens should grow from a private practice-review tool into a local-first music practice intelligence platform. The project should not jump directly to a large ML/DL system. Each milestone should add one product capability through small, reviewable PRs.

## Product position

Current position:

> PracticeLens is a private practice-review tool for musicians who can already attempt a phrase, riff, or take and want objective feedback before asking other people.

It is currently strongest for monophonic or near-monophonic practice review. Polyphony, chords, heavy effects, beginner tutoring, and full transcription are future directions, not current promises.

See also:

- `docs/product_positioning.md`

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
- improved batch/session Markdown review UX;
- optional API workflows for `/health`, `/analyze`, `/compare-batch`, and `/practice-session`;
- typed API payload contracts;
- CI and contributor-facing repo hygiene.

## Immediate execution focus

The next milestone should be:

```text
M1 — Real Audio Readiness
```

The goal is to answer the first real product question:

> What happens when a musician gives PracticeLens real guitar or vocal recordings instead of generated demo data?

M1 should make real usage honest, documented, and safer. It should add suitability checks and warnings before the project expands into larger ML/DL or polyphonic work.

### M1 — Real Audio Readiness

Small PR sequence:

- PR1.1 — Real audio usage guide
- PR1.2 — Input suitability summary
- PR1.3 — Duration mismatch diagnostic
- PR1.4 — Leading silence / start offset diagnostic
- PR1.5 — Low-confidence warnings in Markdown
- PR1.6 — Real audio smoke workflow docs
- PR1.7 — Real-audio manual checklist

## Near-term milestones

### M2 — Practice Review UX v2

Goal: make feedback more useful as practice guidance, not just report text.

Possible small PRs:

- rewrite `practice_plan.md` around action;
- add `Before next take` section;
- explain why a recurring weakness matters;
- add per-take `Keep / Fix / Retry` summaries;
- clarify that the best take is only best among submitted takes;
- add Markdown snapshot tests for UX sections.

### M3 — Progress Tracking v2

Goal: make repeated sessions useful over time.

Possible small PRs:

- add a progress summary model;
- improve `sessions compare` output;
- add progress Markdown rendering;
- add `sessions compare --out`;
- add a simple `sessions trend` command;
- add progress contract tests.

### M4 — Instrument Profiles v1

Goal: stop treating every source as the same instrument.

Possible small PRs:

- add `instrument_profile` config;
- support `guitar_clean`, `vocal`, `bass`, `keyboard`, and `generic` profiles;
- add profile-specific feedback wording;
- add profile-specific suitability warnings;
- document supported profiles;
- test profile selection through CLI/API/reports.

## Capability milestones

### M5 — Music Event Layer v1

Goal: move from frame-only analysis toward musical events.

Possible small PRs:

- add `MusicEvent` model;
- extract event-like attacks/rests/sustains from existing DSP features;
- write `events.json` artifact;
- summarize events in Markdown;
- prototype event alignment;
- use events for missing-first-note diagnostics.

### M6 — Pluggable Analysis Backends

Goal: prepare the architecture for ML/DL without replacing the deterministic baseline.

Possible small PRs:

- define `FeatureExtractor` interface;
- define `AlignmentEngine` interface;
- define `ScoringEngine` interface;
- add backend registry/config;
- add backend metadata to reports;
- prove default output remains unchanged.

### M7 — ML-Assisted Monophonic Review

Goal: improve single-line pitch/onset/timing review through optional local ML backends.

Possible small PRs:

- add optional ML backend contract;
- add `practicelens doctor --ml`;
- add explicit unavailable-backend behavior;
- document local-first ML backend policy;
- add one real optional pitch backend;
- add DSP-vs-ML comparison artifacts.

### M8 — Chords / Polyphony v1

Goal: support first-pass harmonic/chord review without pretending to solve full transcription.

Possible small PRs:

- add `analysis_mode = monophonic | polyphonic_v1`;
- add chroma/pitch-class features;
- add `harmonic_match` metric;
- add chord-friendly report wording;
- add synthetic chord fixtures;
- add polyphonic batch tests;
- document what `polyphonic_v1` can and cannot judge.

### M9 — Note / Chord Event Representation v2

Goal: create a stronger event timeline for future transcription-aware review.

Possible small PRs:

- add `NoteEvent` model;
- add `ChordEvent` model;
- write `music_timeline.json`;
- add timeline Markdown summary;
- add timeline alignment;
- test event-level comparison on generated fixtures.

### M10 — Effect-Aware Recording Profiles

Goal: handle guitar recording realities such as distortion, delay, reverb, and compression with explicit caveats.

Possible small PRs:

- add `recording_profile` config;
- add effect suitability warnings;
- add noise/spectral diagnostics;
- document recording profiles;
- add `Recording caveats` report section;
- test warnings with generated noisy/effected fixtures.

## Product and ecosystem milestones

### M11 — Product Surface v1

Goal: make PracticeLens easier to use as a local product, not only as a library/CLI.

Possible small PRs:

- add `practicelens init`;
- load local project config;
- add simpler CLI aliases if they do not break existing commands;
- add local HTML report export;
- add `practicelens open` helper;
- add install/quickstart docs.

### M12 — HDE Skill Signal Export

Goal: let PracticeLens stand beside a Human Development Environment as a focused music-practice signal source.

Possible small PRs:

- define HDE skill signal contract;
- write `hde_skill_signal.json`;
- add `--export-skill-signal`;
- add skill signal pointers to `session_manifest.json`;
- document PracticeLens' role inside HDE;
- add contract tests.

### M13 — Tutor Mode v0

Goal: cautiously support less confident users without pretending to be a full teacher.

Possible small PRs:

- document tutor mode boundaries;
- add practice breakdown renderer;
- add beginner-friendly feedback wording;
- add slow-practice recommendations;
- test tutor-mode Markdown.

### M14 — Advanced ML/DL Practice Intelligence

Goal: establish the evaluation and backend contracts needed before larger learned review models.

Possible small PRs:

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
M1 — Real Audio Readiness
```

## Explicitly not immediate

The project should not immediately prioritize:

- cloud-first infrastructure;
- social features;
- beginner tutor mode;
- full transcription;
- polyphonic-first redesign;
- large model dependency by default;
- HDE integration before real-audio usefulness is proven.

## Practical north star

PracticeLens should become:

- private by default;
- local-first;
- useful on real practice recordings;
- honest about confidence and limitations;
- extensible toward instrument-aware, polyphonic, and ML/DL-assisted review;
- eventually able to emit meaningful music-practice signals for HDE.
