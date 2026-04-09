# PracticeLens Report

## At a glance

- **Status:** success
- **Mode:** reference
- **Take:** `take_take2.wav`
- **Overall score:** 86.1/100
- **Performance band:** Strong

Strong reference match overall. Best area: Pitch Fidelity (90.0/100). Main improvement area: Timing Consistency (79.0/100).

## Inputs

- Reference: `samples/reference.wav`
- Take: `samples/take_take2.wav`

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
- Findings:
  - [info] Opening phrase is stable and close to the reference.

### Section 1 (8.00s - 16.00s)

- Section average: 80.8/100
- Component breakdown:
  - Pitch Fidelity: 88.0/100
  - Rhythm Fidelity: 78.0/100
  - Timing Consistency: 74.0/100
  - Section Stability: 83.0/100
- Findings:
  - [notice] Small timing drift appears here and slightly compresses phrase spacing.

### Section 2 (16.00s - 24.00s)

- Section average: 86.8/100
- Component breakdown:
  - Pitch Fidelity: 90.0/100
  - Rhythm Fidelity: 84.0/100
  - Timing Consistency: 81.0/100
  - Section Stability: 92.0/100
- Findings:
  - [info] Ending section recovers well and stays controlled.

## Artifacts

- **json_report**: `examples/results/single/report.json` — Structured analysis report.
- **markdown_report**: `examples/results/single/report.md` — Human-readable analysis report.
- **csv_report**: `examples/results/single/report.csv` — Section-level table export.
- **svg_report**: `examples/results/single/report.svg` — Compact visual score summary.
