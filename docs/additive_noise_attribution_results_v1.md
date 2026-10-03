# R0.5g — Additive Noise Attribution Results v1

Status: complete / additive-noise source localized

Frozen production revision:

`4b979d01256598657f19a1cb97ae86dc66470e9b`

Machine-readable snapshot:

`docs/additive_noise_attribution_baseline_v1.json`

## Executive result

The remaining additive-noise nuisance is not one shared failure.

```text
noise -> pitch_fidelity
    begins in pitch feature extraction
    production DTW partially compensates it

noise -> rhythm_fidelity
    begins in onset feature extraction
    alignment is not involved
```

Score reconstruction is exact within the audit epsilon for every condition.

## Pitch fidelity

Recorded attribution:

```text
feature_extraction_with_alignment_contribution
```

Maximum score movement:

```text
production DTW      3.560936
linear alignment    3.799267
alignment effect    1.532031
```

The linear-alignment counterfactual keeps the same noisy extracted pitch features but removes feature-similarity path selection.

Its larger score movement shows that the production DTW is generally **compensating** noise-induced pitch-estimation error rather than creating it.

### Pre-alignment evidence

Mean relative-position pitch error:

```text
noise 0.00   0.000 cents
noise 0.01   4.504 cents
noise 0.03   4.609 cents
noise 0.06   7.599 cents
```

Across the full series:

```text
voiced mismatch fraction = 0
voiced ratio delta        = 0
```

So the nuisance does not first appear as a voiced/unvoiced decision failure.

It appears as frequency-estimate movement inside frames that remain voiced.

### Production DTW compensation

Production aligned mean cents error:

```text
noise 0.00   0.000
noise 0.01   1.440
noise 0.03   2.850
noise 0.06   7.122
```

At low noise the flexible production path substantially reduces the feature error seen by the pitch score.

At the strongest noise level the compensation becomes small:

```text
linear score delta       -3.799267
production score delta   -3.560936
difference               +0.238330
```

### Architectural implication

The remaining pitch nuisance is **not primarily an alignment defect**.

The first observable failure is the deterministic frame-level pitch estimate itself.

A future robustness repair, if justified, should therefore start with the pitch estimator rather than with score tolerance or another global DTW change.

This still does not imply that the frame-level representation must be replaced. The evidence currently identifies estimator robustness, not missing event semantics.

## Rhythm fidelity

Recorded attribution:

```text
feature_extraction
```

Rhythm scoring does not consume alignment, so the attribution is structurally simpler.

For noise 0.01 and 0.03:

```text
reference onset count   23
take onset count        23
normalized onset shift  ~0.00015
score movement          ~0.09-0.10
```

This is a very small onset-location effect.

At noise 0.06:

```text
reference onset count   23
take onset count        24
count penalty           1 / 23 = 0.043478
count score             95.652174
distance score          99.869463
final rhythm score      98.815141
total score delta       -1.184859
```

The score loss decomposes into approximately:

```text
extra-onset count term   1.086957 points   (~91.7%)
onset-location term      0.097903 points   (~8.3%)
```

So the high-noise rhythm failure is dominated by **one spurious detected onset**.

### Architectural implication

The current rhythm nuisance is an onset-detector robustness boundary.

It is not a DTW problem and does not justify changing timing alignment.

Again, this does not yet justify a new event representation: the current evidence points to a bounded detection error in the existing onset feature path.

## Score construction

R0.5g reconstructs the current pitch and rhythm scores term by term.

Recorded reconstruction error:

```text
pitch production max abs error   0
pitch linear max abs error       0
rhythm max abs error             0
```

Therefore no unexplained score-construction effect is needed to account for the observed nuisance.

The existing score formulas are faithfully mapping the noisy feature evidence they receive.

## What R0.5g eliminates

The audit rules out several broad explanations:

- additive-noise pitch movement is not caused primarily by DTW;
- pitch noise is not a voiced-mask instability in this controlled range;
- rhythm noise is not caused by alignment;
- the strongest rhythm failure is not primarily onset-position drift;
- score construction does not introduce unexplained movement.

The remaining defects are now much narrower:

```text
pitch:
    frame-level frequency estimate robustness

rhythm:
    onset detector robustness
    especially spurious onset admission at stronger noise
```

## Representation implication

R0.5c-f already showed that the main timing failures can be resolved inside alignment-space using the same frame-level features.

R0.5g now shows that the remaining additive-noise failures originate in bounded feature estimators rather than in evidence that musical events are fundamentally unobservable.

Taken together, the current machine-side evidence does **not** require immediate admission of an Event / Attack / Sustain / Transition / Rest representation.

A new representation may still become useful later, but it should not be introduced merely to solve the failures observed so far.

## Recommended next step

The strongest next step is **R0.6 — Representation Admission Decision v1**, not another immediate repair PR.

R0.6 can now evaluate the accumulated evidence:

- recording-start equivalence was repaired in preprocessing;
- timing cross-talk was localized to shared alignment ownership;
- metric-specific alignment resolves the tested timing conflict without new features;
- additive-noise pitch failure is estimator-local;
- additive-noise rhythm failure is onset-detector-local;
- the remaining frame-boundary pitch effect under local timing warp is small in production and still lacks R0.5b human significance evidence.

A conservative admissibility decision can therefore be made without first tuning another pitch or onset estimator.

Any future noise-robust estimator work can be justified separately if R0.6 retains the current representation.

## Human evidence boundary

R0.5b remains pending.

R0.5g is synthetic causal attribution. It does not establish how these score movements compare with real within-session musician variability.
