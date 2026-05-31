# Real Audio Usage Guide

This guide explains how to try PracticeLens with real musician recordings.

PracticeLens is currently a private practice-review tool. It works best when you can already attempt the phrase, riff, or vocal line and want objective feedback before asking another person.

It is not yet a beginner tutor, full transcription engine, chord/polyphony judge, DAW, or human-level musical reviewer.

For a short copyable smoke workflow with placeholder paths, see [`examples/real_audio/README.md`](../examples/real_audio/README.md).

## Best current use case

Use PracticeLens when you have:

- one reference recording of the same phrase;
- two or more complete takes of your own attempt;
- a short phrase, riff, vocal line, or exercise that you can play from beginning to end;
- a desire to choose the strongest take and identify the next focused practice target.

A good first real test is:

```text
5-15 seconds
same phrase in every file
clean or mostly dry sound
no long unrelated intro or outro
no restart in the middle of a take
```

## What to record

### Reference

The reference should be the version you want to compare against.

Good references:

- your own best clean take;
- a teacher's recording of the same phrase;
- a dry guitar/vocal example recorded for practice;
- a short exported phrase from your DAW.

Avoid using a full commercial song as the first reference. It may contain drums, bass, vocals, effects, mastering, and arrangement details that PracticeLens is not currently designed to separate.

### Takes

Each take should be one complete attempt at the same phrase.

Good takes:

- `take_01.wav` — one complete attempt;
- `take_02.wav` — another complete attempt;
- `take_03.wav` — another complete attempt.

Avoid takes that contain:

- tuning before the phrase;
- talking;
- long silence;
- a false start followed by a restart;
- unrelated riffs before or after the target phrase;
- a different tempo target or different backing situation than the reference.

## Recommended phrase length

Start short.

Recommended first tests:

```text
5-15 seconds: best
15-30 seconds: usually okay
30+ seconds: possible, but harder to interpret
```

Longer recordings make it harder to tell whether the result reflects musical improvement or unrelated recording differences.

For a full song, split the work into smaller phrases:

```text
riff_a.wav
riff_b.wav
chorus_phrase.wav
solo_fragment_01.wav
```

Then review each phrase separately.

## Silence and count-ins

A small amount of silence before or after the phrase is okay. PracticeLens trims leading and trailing silence during preprocessing.

Still, the best files are tight:

```text
acceptable: short silence before the first note
better: phrase starts clearly after a small buffer
avoid: several seconds of silence, noise, tuning, or talking
```

If the first note is very weak or missing, the analysis may become less reliable. Future M1 diagnostics will make this more explicit, but for now you should manually check whether the first attack is present and clear.

## Metronome and backing tracks

Keep the reference and takes consistent.

Good:

```text
reference: dry guitar phrase
all takes: dry guitar phrase
```

Also okay:

```text
reference: guitar phrase with the same metronome click
all takes: guitar phrase with the same metronome click
```

Risky:

```text
reference: dry guitar phrase
takes: guitar plus loud metronome
```

Very risky:

```text
reference: full backing track
takes: guitar recorded over backing track
```

PracticeLens does not currently separate stems. If drums, bass, vocals, or loud backing tracks are present in only some files, the comparison may become misleading.

## Guitar recording expectations

PracticeLens currently works best with clean or mostly clean single-line guitar material.

Best first tests:

- single-note riffs;
- melodies;
- short licks;
- simple arpeggio-like lines;
- clean DI or clean microphone recording.

More difficult today:

- dense chords;
- heavy distortion;
- delay/reverb-heavy tone;
- chorus/modulation effects;
- fast strummed rhythm parts;
- overlapping strings that make the pitch ambiguous.

Chords, polyphony, and effect-aware review are roadmap items, not current promises.

## Vocal recording expectations

PracticeLens can be useful for dry vocal phrase review when the reference and takes contain the same phrase.

Best first tests:

- short vocal line;
- dry vocal recording;
- clear pitch center;
- similar timing target across reference and takes.

More difficult today:

- loud room noise;
- heavy reverb/delay;
- harmonies;
- double-tracked vocals;
- full mix vocals with instruments underneath.

## Copyable CLI example

For a fuller real-audio smoke workflow with local/private folder layout, placeholder variables, and session-history commands, see [`examples/real_audio/README.md`](../examples/real_audio/README.md).

Folder layout:

```text
samples/real_audio/
  reference.wav
  take_01.wav
  take_02.wav
  take_03.wav
```

Run a practice session:

```bash
practicelens practice-session \
  --reference samples/real_audio/reference.wav \
  --take samples/real_audio/take_01.wav \
  --take samples/real_audio/take_02.wav \
  --take samples/real_audio/take_03.wav \
  --out out/real-audio-session-001 \
  --history-index .practicelens/sessions/index.jsonl
```

Open these first:

```text
out/real-audio-session-001/practice_plan.md
out/real-audio-session-001/batch_report.md
out/real-audio-session-001/session_manifest.json
```

Use the generated take folders for deeper inspection:

```text
out/real-audio-session-001/takes/
```

List indexed sessions:

```bash
practicelens sessions list \
  --history-index .practicelens/sessions/index.jsonl \
  --limit 5
```

Show one session:

```bash
practicelens sessions show 1 \
  --history-index .practicelens/sessions/index.jsonl
```

Compare two sessions after you record another practice session:

```bash
practicelens sessions compare 1 2 \
  --history-index .practicelens/sessions/index.jsonl
```

## How to interpret the result

Use the result as a private practice lens, not as a final musical verdict.

Start with:

1. `practice_plan.md` — what to practice before the next take;
2. `batch_report.md` — which take won and why;
3. the best take's `report.md` — deeper details;
4. the weakest take's `practice_plan.md` — what to fix first.

Remember:

- best take means best among the submitted takes;
- a low score may mean the take is different, noisy, incomplete, or hard to align;
- confidence warnings should be taken seriously;
- real audio with effects or backing tracks can reduce reliability.

## What currently works best

Current best fit:

```text
clean guitar or vocal phrase
short duration
same phrase in all files
complete attempts
minimal effects
minimal backing track mismatch
```

Current weaker fit:

```text
beginner false starts
long recordings
full songs
heavy effects
chords/polyphony
full mixes
unrelated intros/outros
```

## What is not supported well yet

PracticeLens does not currently promise:

- full polyphonic transcription;
- accurate chord-by-chord judging;
- effect-aware tone review;
- source separation from a full mix;
- fingering or tab guidance;
- beginner tutor mode;
- human-level musical taste or expression judgment.

Those are future directions. The current goal is to make private reference-based practice review useful and honest.

## Manual checklist before trusting a result

Use this checklist before treating a real-audio report as practice guidance.

```text
[ ] Reference and every take contain the same phrase, riff, line, or exercise.
[ ] Every take is one complete attempt from beginning to end.
[ ] There is no restart, false start, or second attempt inside the take.
[ ] There is no long unrelated intro, outro, tuning, talking, or noodling.
[ ] The first note or attack is present and clear enough to detect.
[ ] Tuning is the same or close enough across the reference and takes.
[ ] Tempo target is similar across files.
[ ] Metronome/backing-track situation is the same across files.
[ ] The signal is clean enough for the selected instrument profile.
[ ] Heavy distortion, reverb, delay, chorus, or full-mix backing is minimal enough to trust the comparison.
[ ] Any confidence or suitability warnings in Markdown reports are understood before acting on detailed feedback.
```

If several boxes are unchecked, rerecord a cleaner short phrase before trusting the result. PracticeLens is meant to support private practice review for material you can already attempt; it is not a beginner tutor or a replacement for musical judgment.

For a copyable local workflow that keeps audio and generated artifacts out of the repository, use [`examples/real_audio/README.md`](../examples/real_audio/README.md).
