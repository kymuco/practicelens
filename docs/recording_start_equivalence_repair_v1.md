# Recording-Start Equivalence Repair v1

Status: R0.5a repair candidate

## Trigger

R0.5a showed that mathematically equivalent leading recording silence produced a larger measurement movement than the R0.4 local timing target:

```text
leading-silence timing delta   7.009045
local timing target response   4.347350
```

The effect was traced to the preprocessing boundary.

## Root cause

The previous pipeline used:

```python
trim_silence(
    samples,
    threshold=0.01,
    pad_samples=hop_length // 4,
)
```

`trim_silence` finds the first/last above-threshold sample and expands the retained window into whatever samples happen to exist around it.

That makes padding depend on the recording container:

```text
phrase begins near file start
    -> requested leading pad clips at index 0

same phrase after leading silence
    -> full leading pad is available
```

For the R0.5a canonical phrase this produced a 55-sample / 3.4375 ms origin difference.

The downstream frame grid therefore changed even though the intended performance did not.

## Repair

The new preprocessing path is:

```text
normalize
  -> trim exactly to detected activity
  -> add fixed zero pre-roll
  -> add fixed zero post-roll
  -> feature extraction
```

The fixed padding remains:

```text
max(1, hop_length // 4)
```

but it is now synthesized after trimming instead of borrowed from the source file.

This makes the prepared audio invariant to how much silence was physically available before or after the phrase.

## Scope

This PR changes only preprocessing ownership of the analysis origin.

It does not change:

- activity threshold;
- score formulas;
- feature extraction;
- DTW alignment;
- confidence/suitability logic;
- R0.5a equivalence criteria.

## Admission criterion

After this repair, rerun the unchanged R0.5a experiment.

The repair is useful only if the recording-window equivalence floor materially decreases without introducing broader regressions.

The previously recorded R0.5a baseline remains immutable evidence and must not be overwritten.
