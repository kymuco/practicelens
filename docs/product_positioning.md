# PracticeLens Product and Research Positioning

PracticeLens is a local-first music-practice observation and measurement system.

Its current product surface remains a private practice-review tool for musicians who can already attempt a phrase, riff, or take. Its research direction is broader and stricter: turn repeated musical practice into compact, evidence-backed observations of change without pretending that an audio score is automatically a measurement of human skill.

PracticeLens is not currently a beginner tutor, transcription engine, DAW, human-level musical judge, or general personal-development system.

## Current product promise

Today PracticeLens can help a musician:

- compare multiple takes against a reference;
- choose the strongest take within the submitted set;
- surface recurring differences and weaknesses;
- get a concrete next recording target;
- keep a local history of practice sessions;
- compare first-pass progress privately.

These workflows are useful product behavior. They are not, by themselves, proof that every named score is a validated measurement construct.

## Research mission

The research mission is:

> Build a bounded, local-first, reproducible measurement instrument for musical skill development.

The target chain is:

```text
recording
  -> observation
  -> derived evidence
  -> candidate measurement
  -> repeated-trial evidence
  -> cautious development inference
```

PracticeLens should preserve the boundary between what was observed, what was mathematically derived, and what was inferred.

See `docs/measurement_rebaseline_v1.md` for the active measurement program.

## Best current use

PracticeLens currently fits best when the user:

- already knows the phrase, riff, vocal line, or part;
- can record several complete attempts;
- uses short clean monophonic or near-monophonic material;
- wants repeatable local feedback;
- wants evidence that can later be compared across sessions.

## Current scientific boundary

The existing score dimensions such as `pitch_fidelity`, `rhythm_fidelity`, `timing_consistency`, and `section_stability` are treated as candidate measurements during the R0 measurement program.

PracticeLens must not silently equate:

```text
score change == skill change
```

Observed change can contain multiple components:

```text
skill-related change
+ execution variability
+ recording variation
+ measurement error
```

The project now prioritizes separating these components before expanding the interpretation layer.

## Relationship to HDE

PracticeLens should remain a focused music-domain sensor.

It may later export compact observations or development evidence such as:

- session completed;
- repeated deviation pattern;
- measurement trend;
- confidence / uncertainty;
- comparison conditions;
- provenance pointers;
- next measurement target.

External systems such as HDE may combine that evidence with broader memory, goals, context, and development models.

PracticeLens should not become the owner of general personal-development reasoning. Its job is to make music-domain evidence trustworthy enough that another system can consume it.

## Long-term position

The long-term value of PracticeLens is not limited to a standalone music product.

If the project demonstrates that repeated human practice can be represented through bounded observations, validated measurements, uncertainty, and longitudinal evidence, the same architecture can be recreated for other skills using domain-specific sensors.

The transferable artifact is the measurement discipline, not a universal scoring model.
