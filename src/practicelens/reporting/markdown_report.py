from __future__ import annotations

from practicelens.domain.models import AnalysisReport


def report_to_markdown(report: AnalysisReport) -> str:
    """Render an analysis report as human-readable Markdown."""

    overall_score = sum(score.score * score.weight for score in report.scores)
    lines: list[str] = []
    lines.append("# PracticeLens Report")
    lines.append("")
    lines.append(f"**Status:** {report.overview.status}")
    lines.append(f"**Mode:** {report.overview.mode.value}")
    lines.append(f"**Overall score:** {overall_score:.1f}/100")
    if report.summary:
        lines.append("")
        lines.append(report.summary)
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- Reference: `{report.inputs.reference_path}`")
    lines.append(f"- Take: `{report.inputs.take_path}`")
    lines.append("")
    lines.append("## Component Scores")
    lines.append("")
    for score in report.scores:
        lines.append(f"- **{score.name.value}**: {score.score:.1f}/100 (weight {score.weight:.2f})")
    lines.append("")
    lines.append("## Metrics")
    lines.append("")
    for metric in report.metrics:
        detail = f" — {metric.detail}" if metric.detail else ""
        lines.append(
            f"- **{metric.name.value}**: {metric.score:.1f}/100 [{metric.severity.value}]{detail}"
        )
    lines.append("")
    lines.append("## Feedback")
    lines.append("")
    for item in report.feedback:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Sections")
    lines.append("")
    for section in report.sections:
        lines.append(
            f"### Section {section.index} ({section.start_s:.2f}s - {section.end_s:.2f}s)"
        )
        lines.append("")
        for score in section.component_scores:
            lines.append(f"- {score.name.value}: {score.score:.1f}/100")
        if section.findings:
            lines.append("")
            lines.append("Findings:")
            for finding in section.findings:
                lines.append(f"- [{finding.severity.value}] {finding.message}")
        lines.append("")
    if report.artifacts:
        lines.append("## Artifacts")
        lines.append("")
        for artifact in report.artifacts:
            description = f" — {artifact.description}" if artifact.description else ""
            lines.append(f"- **{artifact.kind.value}**: `{artifact.path}`{description}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
