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
- Summary: Strongest overall take with the most stable middle phrase and the cleanest ending.
- Artifacts: 4

### #2 `take_01.wav`

- Score: 84.7/100
- Summary: Good reference match, but timing begins to loosen through the center of the take.
- Artifacts: 4

### #3 `take_03.wav`

- Score: 78.9/100
- Summary: Pitch remains serviceable, but rhythmic stability and timing consistency fall behind the other takes.
- Artifacts: 4

## Batch Artifacts

- **json_report**: `examples/results/batch/batch_report.json`
- **markdown_report**: `examples/results/batch/batch_report.md`
- **csv_report**: `examples/results/batch/batch_report.csv`
