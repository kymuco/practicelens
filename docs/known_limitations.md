# Known Limitations

PracticeLens is pre-alpha software. It is useful for private reference-based practice review, but it is not a complete music-learning platform or a human-level musical judge.

This document describes the current boundaries so users can interpret reports correctly.

## Current best fit

PracticeLens currently works best with:

- short phrases, riffs, vocal lines, or exercises;
- one reference recording of the same material;
- two or more complete takes;
- clean or mostly dry recordings;
- monophonic or near-monophonic material;
- similar tempo target across reference and takes;
- minimal backing-track mismatch;
- no false starts, restarts, or unrelated material inside the take.

A good first real-audio test is:

```text
5-15 seconds
same phrase in every file
clean or mostly dry sound
one complete attempt per take
clear first note or attack
```

## Current weaker fit

PracticeLens is less reliable with:

- long recordings;
- full songs;
- takes with multiple attempts in one file;
- tuning, talking, noodling, or unrelated intros/outros;
- missing or very weak first notes;
- loud room noise, pickup noise, or handling noise;
- strong tempo drift;
- different backing-track or metronome conditions across files;
- full commercial mixes;
- dense chords and polyphony;
- heavy distortion, delay, reverb, chorus, or modulation effects.

The tool can still produce a report in some of these cases, but the result should be interpreted cautiously.

## Not a transcription engine

PracticeLens does not currently promise:

- full note transcription;
- chord-by-chord transcription;
- tab or fingering generation;
- score following;
- source separation from a full mix;
- reliable polyphonic note detection.

Future roadmap milestones may add note/chord event representations and polyphonic review, but the current product is not a full transcription system.

## Not a beginner tutor yet

PracticeLens assumes the user can already attempt the target phrase.

It does not currently teach material from zero. It does not provide full lesson plans, fingering, posture guidance, technique diagnosis, or human teacher judgment.

Future tutor-mode work should make feedback easier to understand, but it should not pretend to replace a teacher.

## Not artistic judgment

PracticeLens reports explainable practice signals such as pitch, rhythm, timing, alignment, section stability, confidence, and input suitability.

It does not judge:

- musical taste;
- emotional expression;
- tone quality in a human sense;
- phrasing intention;
- genre authenticity;
- whether a performance is artistically good.

Use PracticeLens as private feedback before social or teacher feedback, not as the final verdict on musical quality.

## Confidence warnings matter

Markdown reports may include recording confidence or input suitability warnings.

Take those warnings seriously. They often mean that the recording setup, input match, or analysis evidence is weak enough that detailed feedback may be misleading.

Common causes include:

- take duration differs substantially from the reference;
- take starts late relative to the reference;
- leading noise appears before musical activity;
- voiced-frame evidence is limited;
- onset evidence is sparse or absent;
- alignment coverage is limited.

When several warnings appear, rerecord a shorter and cleaner phrase before trusting detailed feedback.

## Privacy and local files

PracticeLens is designed around local-first practice review. User recordings, generated reports, session histories, and manifests should remain local unless the user explicitly chooses otherwise.

Do not commit real user audio or generated private practice artifacts to the repository.

For a safe manual workflow, see `examples/real_audio/README.md`.

## Roadmap boundaries

Future roadmap items include instrument profiles, music events, optional ML backends, polyphony, effect-aware recording profiles, local product surfaces, and high-level skill signal exports.

These are roadmap directions, not current promises.

The current priority is to make the core private practice-review loop useful and honest before expanding into larger AI, transcription, or platform features.
