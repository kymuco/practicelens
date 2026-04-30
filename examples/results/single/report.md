# PracticeLens Report

## At a glance

- **Status:** completed
- **Mode:** reference
- **Take:** `take_take2.wav`
- **Overall score:** 86.1/100
- **Performance band:** Strong
- **Analysis confidence:** High
- **Practice loops:** 2 recommended
- **Next practice step:** loop Section 1 (8.00s - 16.00s) and focus on Timing Consistency. Tighten phrase timing so the take stops drifting across the section.

Strong reference match overall. Best area: Pitch Fidelity (90.0/100). Main improvement area: Timing Consistency (79.0/100).

## Inputs

- Reference: `samples/reference.wav`
- Take: `samples/take_take2.wav`

## Analysis Confidence

- Level: **High**
- Reasons:
  - Alignment coverage is broad enough for a stable reference-aware comparison.
  - Voiced-frame coverage is sufficient for pitch-related feedback.
  - Onset evidence is present for rhythm-oriented feedback.
  - Section reports were produced, so local practice guidance has supporting spans.
- Limitations:
  - PracticeLens v0.1 uses deterministic signal-processing heuristics, not human musical judgment.
  - Confidence is a sanity note for the current evidence quality, not a scientific accuracy guarantee.

## Practice Loops

### Section 1 (8.00s - 16.00s)

- Focus: Timing Consistency
- Instruction: Loop Section 1 (8.00s - 16.00s) and focus on Timing Consistency. Tighten phrase timing so the take stops drifting across the section.

### Section 2 (16.00s - 24.00s)

- Focus: Timing Consistency
- Instruction: Loop Section 2 (16.00s - 24.00s) and focus on Timing Consistency. Tighten phrase timing so the take stops drifting across the section.

## Component Scores

| Component | Score | Weight |
| --- | ---: | ---: |
| Pitch Fidelity | 90.0/100 | 35% |
| Rhythm Fidelity | 82.0/100 | 30% |
| Timing Consistency | 79.0/100 | 20% |
| Section Stability | 88.0/100 | 15% |

## Metrics

| Metric | Score | Severity | Detail |
| --- | ---: | --- | --- |
| Pitch Fidelity | 90.0/100 | info | Stable contour with only small deviations around the middle phrase. |
| Rhythm Fidelity | 82.0/100 | notice | Slight rhythmic looseness appears before the final section. |
| Timing Consistency | 79.0/100 | notice | Timing drift is small but visible in the center of the take. |
| Section Stability | 88.0/100 | info | Section-to-section consistency remains strong overall. |

## Top Strengths

- Pitch Fidelity is a clear current strength at 90.0/100; keep preserving that control.
- Section Stability is a clear current strength at 88.0/100; keep repeating that steadiness across the full take.

## Top Weaknesses

- Timing Consistency is the main weakness at 79.0/100. Tighten phrase timing so the take stops drifting across the section.
- Rhythm Fidelity is the next weakness at 82.0/100. Rehearse the onset pattern slower and re-lock attacks against the reference.

## Next Practice Step

Next practice step: loop Section 1 (8.00s - 16.00s) and focus on Timing Consistency. Tighten phrase timing so the take stops drifting across the section.

## Feedback

- Keep leaning on Pitch Fidelity; it is currently the clearest strength in the take.
- Primary focus area: Timing Consistency. Tighten phrase timing so the take stops drifting across the section.
- Overall the take is strong; preserve the current strengths while improving one weaker area at a time.

## Sections

### Section 0 (0.00s - 8.00s)

- Section average: 86.2/100
- Component breakdown:
  - Pitch Fidelity: 91.0/100
  - Rhythm Fidelity: 84.0/100
  - Timing Consistency: 82.0/100
  - Section Stability: 88.0/100
- Findings: none

### Section 1 (8.00s - 16.00s)

- Section average: 80.8/100
- Component breakdown:
  - Pitch Fidelity: 88.0/100
  - Rhythm Fidelity: 78.0/100
  - Timing Consistency: 74.0/100
  - Section Stability: 83.0/100
- Findings:
  - [notice] Best focus here: Timing Consistency. Tighten phrase timing so the take stops drifting across the section.

### Section 2 (16.00s - 24.00s)

- Section average: 86.8/100
- Component breakdown:
  - Pitch Fidelity: 90.0/100
  - Rhythm Fidelity: 84.0/100
  - Timing Consistency: 81.0/100
  - Section Stability: 92.0/100
- Findings:
  - [notice] Best focus here: Timing Consistency. Tighten phrase timing so the take stops drifting across the section.

## Artifacts

- **json_report**: `examples/results/single/report.json` — Structured analysis report.
- **markdown_report**: `examples/results/single/report.md` — Human-readable analysis report.
- **csv_report**: `examples/results/single/report.csv` — Section-level table export.
- **svg_report**: `examples/results/single/report.svg` — Compact visual score summary.
