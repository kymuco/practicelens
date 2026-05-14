# Showcase Review Notes

The evaluation showcase is useful only if it helps reviewers judge PracticeLens behavior, not merely generate files.

Use this document as a lightweight manual review checklist after running:

```bash
make generate-evaluation-showcase
```

Generated outputs are written under:

```text
examples/evaluation_showcase/generated/
```

## Review path

Start with these files, in this order:

1. `examples/evaluation_showcase/generated/summary.json`
2. `examples/evaluation_showcase/generated/batch/batch_report.md`
3. `examples/evaluation_showcase/generated/single/exact_take/report.md`
4. `examples/evaluation_showcase/generated/single/pitch_drift_take/report.md`
5. `examples/evaluation_showcase/generated/single/timing_drift_take/report.md`
6. `examples/evaluation_showcase/generated/single/rhythm_mistake_take/report.md`
7. `examples/evaluation_showcase/generated/single/tempo_mismatch_take/report.md`

## High-level questions

Ask these before looking at implementation details:

- Does the exact take behave like a strong control case?
- Do degraded cases rank below the exact take?
- Does the reported main weakness roughly match the synthetic case intent?
- Do practice loops point to a plausible section and focus metric?
- Does analysis confidence stay honest about evidence quality?
- Does the batch report help decide what take to keep and what to practice next?

## Case review checklist

| Case | Expected review question |
| --- | --- |
| `exact_take` | Does it score strongly and avoid inventing dramatic weaknesses? |
| `pitch_drift_take` | Does pitch-related feedback become more prominent than timing-only feedback? |
| `timing_drift_take` | Does timing consistency show up as a meaningful weakness? |
| `rhythm_mistake_take` | Does rhythm/onset feedback appear in the report or practice loop? |
| `tempo_mismatch_take` | Does the report expose timing or alignment pressure without pretending the take is clean? |

## Report quality checklist

For each single-take report, check:

- `overall_score` is within a plausible band for the case.
- `top_strengths` are not empty and do not contradict the obvious synthetic defect.
- `top_weaknesses` mention a useful focus area.
- `next_practice_step` is concrete enough to act on.
- `practice_loops` include section spans, focus metrics, and instructions.
- `analysis_confidence.reasons` are specific enough to explain why the report is usable.
- `analysis_confidence.limitations` make the deterministic v0.1 caveat visible.
- Markdown output is readable without opening the JSON.

## Batch review checklist

For `batch/batch_report.md`, check:

- Ranking order looks plausible.
- The best take is clearly named.
- Delta vs best is easy to read.
- Each take summary includes at least one actionable practice loop when relevant.
- The report helps answer both:
  - which take is strongest;
  - what should be practiced next.

## Red flags to capture

If any of these appear, capture them in a follow-up issue or PR note:

- exact take receives a surprisingly low score;
- degraded cases rank above exact take without a clear reason;
- expected weakness and reported weakness consistently disagree;
- practice loops always point to the same section regardless of case;
- confidence is high even when evidence looks sparse or unstable;
- Markdown is too noisy for a musician to read quickly;
- batch ranking is technically correct but practically unhelpful.

## Known limitations of this review

This showcase is synthetic. It does not prove real-world musical correctness.

It does not cover:

- noisy microphone recordings;
- real singing vibrato and phrasing;
- guitar pick noise and fret artifacts;
- polyphonic material;
- different room acoustics;
- different skill levels;
- human preference or artistic interpretation.

A passing showcase review means only this:

> PracticeLens behaves plausibly on deterministic synthetic cases and is ready for broader real-audio evaluation.

It does not mean the scoring model is musically validated.

## Suggested follow-up after review

If the showcase looks coherent, the next useful step is a small real-audio evaluation pack outside the repository or with explicitly safe generated/owned recordings.

That future pack should compare PracticeLens output against human notes for a handful of short takes.
