from __future__ import annotations

from practicelens.domain.models import AnalysisReport


def report_to_markdown(report: AnalysisReport) -> str:
    """Render an analysis report as human-readable Markdown."""

    overall_score = sum(score.score * score.weight for score in report.scores)
    take_name = report.inputs.take_path.name
    lines: list[str] = []
    lines.append("# PracticeLens Report")
    lines.append("")
    lines.append("## At a glance")
    lines.append("")
    lines.append(f"- **Status:** {report.overview.status}")
    lines.append(f"- **Mode:** {report.overview.mode.value}")
    lines.append(f"- **Take:** `{take_name}`")
    lines.append(f"- **Overall score:** {overall_score:.1f}/100")
    lines.append(f"- **Performance band:** {_score_band(overall_score)}")
    lines.append(f"- **Analysis confidence:** {report.analysis_confidence.level.title()}")
    if report.practice_loops:
        lines.append(f"- **Practice loops:** {len(report.practice_loops)} recommended")
    if report.next_practice_step:
        step_summary = report.next_practice_step.removeprefix("Next practice step: ")
        lines.append(f"- **Next practice step:** {step_summary}")
    if report.summary:
        lines.extend(["", report.summary])

    lines.extend(["", "## Inputs", ""])
    lines.append(f"- Reference: `{report.inputs.reference_path}`")
    lines.append(f"- Take: `{report.inputs.take_path}`")

    lines.extend(["", "## Analysis Confidence", ""])
    lines.append(f"- Level: **{report.analysis_confidence.level.title()}**")
    if report.analysis_confidence.reasons:
        lines.append("- Reasons:")
        for reason in report.analysis_confidence.reasons:
            lines.append(f"  - {reason}")
    if report.analysis_confidence.limitations:
        lines.append("- Limitations:")
        for limitation in report.analysis_confidence.limitations:
            lines.append(f"  - {limitation}")

    lines.extend(["", "## Practice Loops", ""])
    if report.practice_loops:
        for loop in report.practice_loops:
            lines.append(f"### Section {loop.section_index} ({loop.start_s:.2f}s - {loop.end_s:.2f}s)")
            lines.append("")
            lines.append(f"- Focus: {_metric_label(loop.focus.value)}")
            lines.append(f"- Instruction: {loop.instruction}")
            lines.append("")
    else:
        lines.append("No focused practice loops were generated.")

    lines.extend(["", "## Component Scores", ""])
    lines.append("| Component | Score | Weight |")
    lines.append("| --- | ---: | ---: |")
    for score in report.scores:
        lines.append(f"| {_metric_label(score.name.value)} | {score.score:.1f}/100 | {int(round(score.weight * 100))}% |")

    lines.extend(["", "## Metrics", ""])
    if report.metrics:
        lines.append("| Metric | Score | Severity | Detail |")
        lines.append("| --- | ---: | --- | --- |")
        for metric in report.metrics:
            detail = metric.detail or "-"
            lines.append(f"| {_metric_label(metric.name.value)} | {metric.score:.1f}/100 | {metric.severity.value} | {detail} |")
    else:
        lines.append("No metric rows were produced.")

    lines.extend(["", "## Top Strengths", ""])
    if report.top_strengths:
        for item in report.top_strengths:
            lines.append(f"- {item}")
    else:
        lines.append("- No strengths were generated.")

    lines.extend(["", "## Top Weaknesses", ""])
    if report.top_weaknesses:
        for item in report.top_weaknesses:
            lines.append(f"- {item}")
    else:
        lines.append("- No weaknesses were generated.")

    lines.extend(["", "## Next Practice Step", ""])
    if report.next_practice_step:
        lines.append(report.next_practice_step)
    else:
        lines.append("No next-step guidance was generated.")

    lines.extend(["", "## Feedback", ""])
    if report.feedback:
        for item in report.feedback:
            lines.append(f"- {item}")
    else:
        lines.append("- No feedback items were generated.")

    lines.extend(["", "## Sections", ""])
    for section in report.sections:
        section_avg = sum(score.score for score in section.component_scores) / max(1, len(section.component_scores))
        lines.append(f"### Section {section.index} ({section.start_s:.2f}s - {section.end_s:.2f}s)")
        lines.append("")
        lines.append(f"- Section average: {section_avg:.1f}/100")
        lines.append("- Component breakdown:")
        for score in section.component_scores:
            lines.append(f"  - {_metric_label(score.name.value)}: {score.score:.1f}/100")
        if section.findings:
            lines.append("- Findings:")
            for finding in section.findings:
                lines.append(f"  - [{finding.severity.value}] {finding.message}")
        else:
            lines.append("- Findings: none")
        lines.append("")

    if report.artifacts:
        lines.append("## Artifacts")
        lines.append("")
        for artifact in report.artifacts:
            description = f" — {artifact.description}" if artifact.description else ""
            lines.append(f"- **{artifact.kind.value}**: `{artifact.path}`{description}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _metric_label(raw_name: str) -> str:
    return raw_name.replace('_', ' ').title()


def _score_band(score: float) -> str:
    if score >= 90.0:
        return 'Excellent'
    if score >= 80.0:
        return 'Strong'
    if score >= 70.0:
        return 'Promising'
    return 'Needs Work'
