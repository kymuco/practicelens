# Baseline Measurement Validity Results v1

Status: R0.4 recorded baseline  
Frozen instrument revision: `1cb1a6d92ada295b989cf41c26c32a434f82a510`

Machine-readable snapshot: `docs/measurement_validity_baseline_v1.json`

## Result summary

The first controlled R0.4 audit produced:

| Family | Role | Verdict | Main result |
| --- | --- | --- | --- |
| `amplitude_gain` | nuisance | PASS | All four component scores remained exactly invariant through 12 dB attenuation magnitude. |
| `deterministic_additive_noise` | nuisance | FAIL | Pitch, timing, and section-stability scores moved; rhythm remained invariant. |
| `local_timing_warp` | target | PARTIAL | Timing responded in the expected direction, but not monotonically; protected pitch also moved. |
| `pitch_drift` | target | PARTIAL | Pitch response was strong and monotonic; protected rhythm and timing scores also moved. |

Family verdict counts:

```text
PASS        1
PARTIAL     2
FAIL        1
UNRESOLVED  0
```

These are strict deterministic synthetic screening verdicts. They are not an overall validity score for PracticeLens.

## Amplitude gain

Strengths:

```text
0 / 3 / 6 / 12 dB attenuation magnitude
```

All audited scores stayed exactly at 100:

```text
pitch_fidelity       100 -> 100 -> 100 -> 100
rhythm_fidelity      100 -> 100 -> 100 -> 100
timing_consistency   100 -> 100 -> 100 -> 100
section_stability    100 -> 100 -> 100 -> 100
```

Strict nuisance invariance: **PASS**.

This result is consistent with the current preprocessing path's peak normalization successfully removing this controlled gain change from downstream scoring.

It does not establish invariance to clipping, microphone nonlinearities, changing noise floors, or other real recording changes.

## Deterministic additive noise

Strengths:

```text
0 / 0.01 / 0.03 / 0.06 full-scale fraction
```

Observed score sequences:

```text
pitch_fidelity
100
99.9336490482
98.9986657278
96.5975651500

rhythm_fidelity
100
100
100
100

timing_consistency
100
98.4914605894
100
97.9526965142

section_stability
100
98.1314208864
99.5569222189
97.3996624122
```

Maximum absolute deltas from control:

```text
pitch_fidelity       3.402435
rhythm_fidelity      0.000000
timing_consistency   2.047303
section_stability    2.600338
```

Strict nuisance invariance: **FAIL**.

The important additional observation is that every condition still reported:

```text
analysis confidence = high
input suitability   = ok
alignment coverage  = 1.0
```

So the current confidence/suitability layer does not flag this nuisance family even when three candidate measurements move.

R0.4 does not yet decide whether these deltas are practically large. R0.5 must establish the empirical noise floor before that claim is possible.

## Local timing warp

Internal boundary shifts:

```text
0 / 20 / 40 / 80 ms
```

Primary measurement:

```text
timing_consistency
```

Observed sequence:

```text
100
95.6526495531
97.7399791762
95.8935595242
```

Endpoint delta:

```text
-4.106440
```

Maximum response:

```text
-4.347350
```

Directional sensitivity: **PASS**.  
Monotonicity: **PARTIAL**.

The 40 ms condition scores better than the 20 ms condition, so the current timing score detects the intervention but does not provide an ordered severity response for this series.

Protected `pitch_fidelity` moved by as much as:

```text
0.576328 points
```

Strict protected specificity: **FAIL**.

Other observed maximum deltas:

```text
rhythm_fidelity      1.294985
section_stability    3.622737
```

This is the first concrete evidence that the current timing representation is sensitive but not cleanly factorized.

## Pitch drift

Terminal drift strengths:

```text
0 / 0.01 / 0.03 / 0.06
```

Primary measurement:

```text
pitch_fidelity
```

Observed sequence:

```text
100
96.6669489152
89.7845092476
75.0652680143
```

Endpoint delta:

```text
-24.934732
```

Directional sensitivity: **PASS**.  
Monotonicity: **PASS**.

This is the cleanest positive result in R0.4: the current pitch score strongly and monotonically tracks increasing synthetic pitch drift.

However, the protected measurements also moved:

```text
max |rhythm_fidelity delta|      2.196657
max |timing_consistency delta|   2.228232
```

Strict protected specificity: **FAIL**.

The cross-talk is also non-monotonic: the protected timing/rhythm deviations are largest at weaker/intermediate drift and mostly recede at the strongest drift.

`section_stability`, which is not treated as independent, moved strongly:

```text
100
96.6516717195
91.6263149452
84.6262466164
```

Maximum delta:

```text
15.373753
```

That behavior is consistent with its current role as a derived aggregate rather than an orthogonal construct.

## What R0.4 establishes

R0.4 gives us four useful boundaries.

### 1. Gain normalization is a genuine strength of the current instrument

The controlled amplitude series disappears completely from all four scores.

### 2. Pitch measurement has a credible controlled sensitivity signal

`pitch_fidelity` shows a large, ordered response to pitch drift.

This does not yet prove real-world construct validity, but it is strong enough that replacing the pitch path wholesale would be unjustified without better evidence.

### 3. Timing measurement is sensitive but not ordinal in the current representation

`timing_consistency` detects the local timing intervention, but its response is not monotonic with intervention magnitude.

That is a concrete measurement limitation, not a UX problem.

### 4. Current candidate dimensions are not strictly independent

Both target experiments produce movement outside their protected dimensions.

The next work should therefore distinguish:

- real physical coupling in the generated signal;
- feature-extractor coupling;
- alignment-induced coupling;
- score-construction coupling;
- practically negligible movement versus meaningful movement.

R0.4 alone cannot separate those explanations.

## What R0.4 does not justify

The results do **not** yet justify:

- replacing the current representation with event/perceptual primitives;
- adding ML;
- treating every nonzero cross-delta as practically important;
- claiming that the current score dimensions measure human skill;
- changing thresholds to make the current instrument pass.

Those decisions remain downstream of repeatability and noise-floor evidence.

## Next research question

R0.5 should answer:

> How much candidate-measurement movement occurs when the intended performance condition is unchanged or equivalent?

Only after that noise floor is known can we say whether, for example, a 0.58-point pitch movement under timing warp is materially problematic while a 24.93-point pitch response to pitch drift is clearly signal-bearing.

That is now the shortest path toward deciding whether the current frame-level representation is sufficient or whether R0.6 should admit a new event/perceptual representation.
