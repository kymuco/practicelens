from __future__ import annotations

from pathlib import Path

from practicelens.domain.enums import ArtifactKind
from practicelens.domain.models import AnalysisReport, ArtifactLink
from practicelens.reporting import (
    report_to_csv_text,
    report_to_json_text,
    report_to_markdown,
    report_to_svg,
)


def write_report_artifacts(
    report: AnalysisReport,
    out_dir: Path,
) -> tuple[AnalysisReport, tuple[ArtifactLink, ...]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "report.json"
    markdown_path = out_dir / "report.md"
    csv_path = out_dir / "report.csv"
    svg_path = out_dir / "report.svg"

    artifacts = (
        ArtifactLink(
            ArtifactKind.JSON_REPORT,
            str(json_path),
            "Structured analysis report.",
        ),
        ArtifactLink(
            ArtifactKind.MARKDOWN_REPORT,
            str(markdown_path),
            "Human-readable analysis report.",
        ),
        ArtifactLink(
            ArtifactKind.CSV_REPORT,
            str(csv_path),
            "Section-level table export.",
        ),
        ArtifactLink(
            ArtifactKind.SVG_REPORT,
            str(svg_path),
            "Compact visual score summary.",
        ),
    )

    report_with_artifacts = AnalysisReport(
        overview=report.overview,
        inputs=report.inputs,
        feature_flags=report.feature_flags,
        scores=report.scores,
        metrics=report.metrics,
        sections=report.sections,
        analysis_confidence=report.analysis_confidence,
        practice_loops=report.practice_loops,
        top_strengths=report.top_strengths,
        top_weaknesses=report.top_weaknesses,
        next_practice_step=report.next_practice_step,
        feedback=report.feedback,
        artifacts=artifacts,
        summary=report.summary,
    )

    json_path.write_text(report_to_json_text(report_with_artifacts), encoding="utf-8")
    markdown_path.write_text(report_to_markdown(report_with_artifacts), encoding="utf-8")
    csv_path.write_text(report_to_csv_text(report_with_artifacts), encoding="utf-8")
    svg_path.write_text(report_to_svg(report_with_artifacts), encoding="utf-8")
    return report_with_artifacts, artifacts
