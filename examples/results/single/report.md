# PracticeLens Report

**Status:** success
**Mode:** reference
**Overall score:** 86.1/100

Strong reference match overall. Minor timing looseness appears in the middle phrase, but pitch stability stays solid and the ending recovers well.

## Inputs

- Reference: `samples/reference.wav`
- Take: `samples/take_take2.wav`

## Component Scores

- **pitch_fidelity**: 90.0/100 (weight 0.35)
- **rhythm_fidelity**: 82.0/100 (weight 0.30)
- **timing_consistency**: 79.0/100 (weight 0.20)
- **section_stability**: 88.0/100 (weight 0.15)

## Metrics

- **pitch_fidelity**: 90.0/100 [info] — Stable contour with only small deviations around the middle phrase.
- **rhythm_fidelity**: 82.0/100 [notice] — Slight rhythmic looseness appears before the final section.
- **timing_consistency**: 79.0/100 [notice] — Timing drift is small but visible in the center of the take.
- **section_stability**: 88.0/100 [info] — Section-to-section consistency remains strong overall.

## Feedback

- Keep the same pitch approach; pitch stability is already strong.
- Focus the next repetition on timing through the middle phrase.
- The ending is one of the strongest parts of the take and should be preserved.

## Sections

### Section 0 (0.00s - 8.00s)

- pitch_fidelity: 91.0/100
- rhythm_fidelity: 84.0/100
- timing_consistency: 82.0/100
- section_stability: 88.0/100

Findings:
- [info] Opening phrase is stable and close to the reference.

### Section 1 (8.00s - 16.00s)

- pitch_fidelity: 88.0/100
- rhythm_fidelity: 78.0/100
- timing_consistency: 74.0/100
- section_stability: 83.0/100

Findings:
- [notice] Small timing drift appears here and slightly compresses phrase spacing.

### Section 2 (16.00s - 24.00s)

- pitch_fidelity: 90.0/100
- rhythm_fidelity: 84.0/100
- timing_consistency: 81.0/100
- section_stability: 92.0/100

Findings:
- [info] Ending section recovers well and stays controlled.

## Artifacts

- **json_report**: `examples/results/single/report.json` — Structured analysis report.
- **markdown_report**: `examples/results/single/report.md` — Human-readable analysis report.
- **csv_report**: `examples/results/single/report.csv` — Section-level table export.
- **svg_report**: `examples/results/single/report.svg` — Compact visual score summary.
