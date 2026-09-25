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

## Candidate A — fixed zero padding

The first repair candidate changed the path to:

```text
normalize
  -> trim exactly to detected activity
  -> add fixed zero pre-roll/post-roll
  -> feature extraction
```

It eliminated recording-window sensitivity completely, but the unchanged R0.5a probe exposed a new regression:

```text
dc-offset timing delta
before candidate A: 0.246074
after candidate A:  4.340076
```

Candidate A therefore failed the admission rule and is not accepted as the final repair.

The reason is that zero padding next to a DC-biased waveform creates an artificial acquisition-boundary step.

## Candidate B1 — unconditional DC centering

Unconditional mean subtraction eliminated the R0.5a DC-offset regression, but the post-repair R0.4 audit exposed a new strict nuisance regression at -12 dB gain:

```text
rhythm_fidelity delta = -0.961538
```

The canonical finite-window mean is only on the order of 10^-6 full scale, so treating that residual as a material sensor DC bias was unnecessary.

Candidate B1 is therefore rejected.

## Candidate B2 — material DC centering plus fixed zero padding

The revised preprocessing path is:

```text
resample if needed
  -> remove constant DC component
  -> peak normalize
  -> trim exactly to detected activity
  -> add fixed zero pre-roll
  -> add fixed zero post-roll
  -> feature extraction
```

The DC-removal step subtracts the sample mean only when its magnitude exceeds `1e-4` full scale.

This deadband separates a material acquisition bias from negligible finite-window residual mean. The R0.5a ±0.01 DC cases remain two orders of magnitude above the admission threshold, while ordinary canonical/gain cases remain untouched.

A constant sensor/acquisition bias is a zero-frequency component and is outside the intended music-performance construct.

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
