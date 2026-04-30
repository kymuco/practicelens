# PracticeLens Batch Compare

## At a glance

- **Reference:** `samples/reference.wav`
- **Compared takes:** 3
- **Best take:** `take_02.wav`
- **Best score:** 88.4/100

Best take: take_02.wav with 88.4/100 across 3 compared takes.

## Ranking

| Rank | Take | Score | Delta vs best | Output dir |
| --- | --- | ---: | ---: | --- |
| 1 | `take_02.wav` | 88.4 | 0.0 | `out/batch/takes/02-take_02` |
| 2 | `take_01.wav` | 84.7 | 3.7 | `out/batch/takes/01-take_01` |
| 3 | `take_03.wav` | 78.9 | 9.5 | `out/batch/takes/03-take_03` |

## Take summaries

### #1 `take_02.wav`

- Score: 88.4/100
- Summary: Strong reference match overall. Best area: Section Stability (91.0/100). Main improvement area: Rhythm Fidelity (84.0/100).
- First practice loop: Loop Section 1 (8.00s - 16.00s) and focus on Rhythm Fidelity. Rehearse the onset pattern slower and re-lock attacks against the reference.
- Practice loops: 1
- Artifacts: 4

### #2 `take_01.wav`

- Score: 84.7/100
- Summary: Strong reference match overall. Best area: Pitch Fidelity (88.0/100). Main improvement area: Timing Consistency (80.0/100).
- First practice loop: Loop Section 1 (8.00s - 16.00s) and focus on Timing Consistency. Tighten phrase timing so the take stops drifting across the section.
- Practice loops: 1
- Artifacts: 4

### #3 `take_03.wav`

- Score: 78.9/100
- Summary: Promising reference match overall. Best area: Pitch Fidelity (81.0/100). Main improvement area: Rhythm Fidelity (73.0/100).
- First practice loop: Loop Section 1 (8.00s - 16.00s) and focus on Rhythm Fidelity. Rehearse the onset pattern slower and re-lock attacks against the reference.
- Practice loops: 1
- Artifacts: 4

## Batch Artifacts

- **json_report**: `examples/results/batch/batch_report.json`
- **markdown_report**: `examples/results/batch/batch_report.md`
- **csv_report**: `examples/results/batch/batch_report.csv`
