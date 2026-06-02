# PracticeLens Batch Compare

## At a glance

- **Reference:** `examples\evaluation_showcase\generated\assets\reference_phrase.wav`
- **Compared takes:** 5
- **Best take:** `exact_take.wav`
- **Best score:** 100.0/100
- **Recurring weakness:** Pitch Fidelity
- **Strongest stable area:** Rhythm Fidelity
- **Next target:** Record one new take that improves Pitch Fidelity while preserving Rhythm Fidelity.

Best take: exact_take.wav with 100.0/100 across 5 compared takes.

## What to do next

1. Keep `exact_take.wav` as the current best take.
2. Practice Pitch Fidelity first.
3. Record next: Record one new take that improves Pitch Fidelity while preserving Rhythm Fidelity.
4. Start with `tempo_mismatch_take.wav` section 4 (4.00s - 5.00s).

## Why this take won

- `exact_take.wav` has the highest overall score in this session.
- It is 12.0 points ahead of `rhythm_mistake_take.wav`.
- Evidence: Excellent reference match overall. Best area: Pitch Fidelity (100.0/100). Main improvement area: Pitch Fidelity (100.0/100).

## Session decision

- **Keep:** `exact_take.wav` (100.0/100).
- **Review weakest take:** `tempo_mismatch_take.wav` (62.2/100).
- **Main recurring weakness:** Pitch Fidelity (5/5 takes).
- **Protect stable area:** Rhythm Fidelity (98.3/100 average).
- **Record next:** Record one new take that improves Pitch Fidelity while preserving Rhythm Fidelity.

## Recommended session loops

1. `tempo_mismatch_take.wav` section 4 (4.00s - 5.00s): Loop Section 4 (4.00s - 5.00s) and focus on Pitch Fidelity. Slow the phrase down and match sustained notes more deliberately against the reference.
2. `tempo_mismatch_take.wav` section 3 (3.00s - 4.00s): Loop Section 3 (3.00s - 4.00s) and focus on Pitch Fidelity. Slow the phrase down and match sustained notes more deliberately against the reference.
3. `tempo_mismatch_take.wav` section 0 (0.00s - 1.00s): Loop Section 0 (0.00s - 1.00s) and focus on Pitch Fidelity. Slow the phrase down and match sustained notes more deliberately against the reference.

## Ranking

| Rank | Take | Score | Delta vs best | Output dir |
| --- | --- | ---: | ---: | --- |
| 1 | `exact_take.wav` | 100.0 | 0.0 | `examples\evaluation_showcase\generated\batch\takes\01-exact_take` |
| 2 | `rhythm_mistake_take.wav` | 88.0 | 12.0 | `examples\evaluation_showcase\generated\batch\takes\04-rhythm_mistake_take` |
| 3 | `pitch_drift_take.wav` | 81.7 | 18.3 | `examples\evaluation_showcase\generated\batch\takes\02-pitch_drift_take` |
| 4 | `timing_drift_take.wav` | 71.4 | 28.6 | `examples\evaluation_showcase\generated\batch\takes\03-timing_drift_take` |
| 5 | `tempo_mismatch_take.wav` | 62.2 | 37.8 | `examples\evaluation_showcase\generated\batch\takes\05-tempo_mismatch_take` |

## Take summaries

### #1 `exact_take.wav`

- Score: 100.0/100
- Summary: Excellent reference match overall. Best area: Pitch Fidelity (100.0/100). Main improvement area: Pitch Fidelity (100.0/100).
- Practice loops: none
- Artifacts: 6

### #2 `rhythm_mistake_take.wav`

- Score: 88.0/100
- Summary: Strong reference match overall. Best area: Timing Consistency (97.4/100). Main improvement area: Pitch Fidelity (78.9/100).
- First practice loop: Loop Section 1 (1.00s - 2.00s) and focus on Rhythm Fidelity. Rehearse the onset pattern slower and re-lock attacks against the reference.
- Practice loops: 1
- Artifacts: 6

### #3 `pitch_drift_take.wav`

- Score: 81.7/100
- Summary: Strong reference match overall. Best area: Rhythm Fidelity (100.0/100). Main improvement area: Pitch Fidelity (58.7/100).
- First practice loop: Loop Section 4 (4.00s - 5.00s) and focus on Pitch Fidelity. Slow the phrase down and match sustained notes more deliberately against the reference.
- Practice loops: 3
- Artifacts: 6

### #4 `timing_drift_take.wav`

- Score: 71.4/100
- Summary: Promising reference match overall. Best area: Rhythm Fidelity (97.8/100). Main improvement area: Pitch Fidelity (56.3/100).
- First practice loop: Loop Section 4 (4.00s - 5.00s) and focus on Pitch Fidelity. Slow the phrase down and match sustained notes more deliberately against the reference.
- Practice loops: 3
- Artifacts: 6

### #5 `tempo_mismatch_take.wav`

- Score: 62.2/100
- Summary: The take diverges noticeably from the reference overall. Best area: Rhythm Fidelity (98.9/100). Main improvement area: Pitch Fidelity (32.2/100).
- First practice loop: Loop Section 4 (4.00s - 5.00s) and focus on Pitch Fidelity. Slow the phrase down and match sustained notes more deliberately against the reference.
- Practice loops: 3
- Artifacts: 6

## Batch Artifacts

- **json_report**: `examples\evaluation_showcase\generated\batch\batch_report.json`
- **markdown_report**: `examples\evaluation_showcase\generated\batch\batch_report.md`
- **csv_report**: `examples\evaluation_showcase\generated\batch\batch_report.csv`
- **svg_report**: `examples\evaluation_showcase\generated\batch\batch_report.svg`
- **practice_plan**: `examples\evaluation_showcase\generated\batch\practice_plan.md`
- **session_manifest**: `examples\evaluation_showcase\generated\batch\session_manifest.json`
