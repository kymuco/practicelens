# R0.5b — Local Session Repeatability v1

Status: protocol + local runner

## Question

R0.5a established zero deterministic movement across the tested synthetic equivalence class after the recording-origin repair.

R0.5b asks the next distinct question:

> When the same musician repeats the same material inside one stable session, with no intended learning interval, how much do the candidate measurements naturally move?

This is performer/session repeatability, not software repeatability.

## Why this is separate from ordinary practice-session UX

The existing PracticeLens batch workflow ranks takes and identifies a best/weakest take.

R0.5b must not rank.

A repeatability experiment treats every independent take as a sample from the same intended session-state. Selecting only the best take would systematically underestimate within-session variation and contaminate the measurement question with product semantics.

## Collection protocol v1

Use one fixed reference and one short musical passage.

Before collecting the measured takes:

1. warm up enough that the passage is comfortable to perform;
2. choose one stable instrument / microphone / interface setup;
3. keep microphone position and input gain unchanged;
4. do not change the reference;
5. do not edit, time-shift, denoise, normalize, or manually trim the take WAVs.

Then collect **8 consecutive independent takes**.

R0.5b accepts a minimum of 5, but 8 is recommended.

During the measured series:

- do not inspect PracticeLens scores between takes;
- do not deliberately practice or correct one diagnosed weakness between takes;
- do not change tempo target, fingering/technique plan, instrument, microphone, or room setup intentionally;
- short ordinary rests are allowed;
- rerecord a take only for an obvious invalid capture such as interruption or missing audio, and record that exclusion locally.

The protocol does not claim that human execution is literally unchanged. It defines a bounded period in which no skill-development interval is intended.

## Local execution

Example:

```powershell
python tools/run_local_session_repeatability.py `
  --reference "W:\practice\reference.wav" `
  --take "W:\practice\take01.wav" `
  --take "W:\practice\take02.wav" `
  --take "W:\practice\take03.wav" `
  --take "W:\practice\take04.wav" `
  --take "W:\practice\take05.wav" `
  --take "W:\practice\take06.wav" `
  --take "W:\practice\take07.wav" `
  --take "W:\practice\take08.wav" `
  --out "out\r0_5b_session_01.json" `
  --session-label "session-01"
```

The analyzer uses the frozen R0 measurement configuration:

```text
target_sample_rate = 16000
frame_length       = 1024
hop_length         = 256
segment_duration_s = 1.0
```

## Integrity guards

The runner rejects:

- fewer than 5 takes;
- missing files;
- any take byte-identical to the reference;
- duplicate take files.

This prevents accidental reuse from artificially lowering the observed repeatability spread.

## Exported evidence

The JSON artifact contains:

- ordinal take IDs such as `take_01`;
- the four candidate measurements per take;
- analysis confidence;
- input-suitability status;
- alignment coverage;
- within-session summary statistics.

It deliberately does **not** contain:

- raw audio;
- local source paths;
- audio fingerprints.

Raw recordings stay local.

## Statistics

For each candidate measurement R0.5b reports:

```text
median
minimum
maximum
observed_span
median_abs_deviation
max_abs_deviation_from_median
median_pairwise_abs_delta
max_pairwise_abs_delta
```

The first robust pair is:

```text
median + median_abs_deviation
```

The conservative observed envelope is:

```text
observed_span == max_pairwise_abs_delta
```

No normal-distribution assumption is made.

## Why one session is not yet a universal noise floor

One session can establish:

> this instrument + this performer + this material + this setup showed this much within-session movement.

It cannot yet establish:

> all future changes smaller than X are noise.

A human-facing minimum detectable longitudinal change requires multiple repeatability sessions, ideally across different days, while separating:

```text
within-session execution variance
between-session setup variance
actual development
```

R0.5b v1 therefore records evidence but does not emit PASS/FAIL or a global threshold.

## Quality evidence

Takes are not silently discarded because confidence or suitability is weaker.

Instead the artifact records:

- counts by suitability status;
- counts by confidence level;
- minimum alignment coverage;
- explicit quality flags.

This prevents a repeatability estimate from looking artificially clean because difficult takes were filtered after observing the scores.

## Interpretation boundary

R0.5b may tell us whether a 0.7-point pitch delta is ordinary within-session movement for one measured session.

It still does not establish that a 5-point difference between two future sessions is caused by learning.

That claim requires a later longitudinal design.

## Admission to R0.6

R0.6 should not decide on a new event/perceptual representation from R0.4 alone.

It should compare:

1. target response magnitudes from R0.4;
2. deterministic equivalence floor from R0.5a;
3. real within-session spread from R0.5b.

Only measurement deficiencies that remain large relative to real repeatability evidence justify changing the representation.
