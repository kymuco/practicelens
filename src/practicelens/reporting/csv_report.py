from __future__ import annotations

import csv
import io

from practicelens.domain.models import AnalysisReport


def report_to_csv_text(report: AnalysisReport) -> str:
    """Render section-level report data as CSV text."""

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "section_index",
            "start_s",
            "end_s",
            "pitch_fidelity",
            "rhythm_fidelity",
            "timing_consistency",
            "section_stability",
            "findings_count",
            "findings",
        ]
    )

    for section in report.sections:
        score_map = {score.name.value: score.score for score in section.component_scores}
        findings_text = " | ".join(finding.message for finding in section.findings)
        writer.writerow(
            [
                section.index,
                f"{section.start_s:.3f}",
                f"{section.end_s:.3f}",
                f"{score_map.get('pitch_fidelity', 0.0):.3f}",
                f"{score_map.get('rhythm_fidelity', 0.0):.3f}",
                f"{score_map.get('timing_consistency', 0.0):.3f}",
                f"{score_map.get('section_stability', 0.0):.3f}",
                len(section.findings),
                findings_text,
            ]
        )

    return buffer.getvalue()
