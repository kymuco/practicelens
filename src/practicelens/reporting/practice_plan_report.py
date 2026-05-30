from __future__ import annotations

from practicelens.domain.models import AnalysisReport, ComponentScore
from practicelens.reporting.markdown_warnings import report_confidence_warning_lines


def report_to_practice_plan_markdown(report: AnalysisReport) -> str:
    """Render a focused practice plan for one analysis report."""

    overall_score = sum(score.score * score.weight for score in report.scores)
    weakest = min(report.scores, key=lambda score: score.score)
    strongest = max(report.scores, key=lambda score: score.score)

    lines: list[str] = [
        "# PracticeLens Practice Plan",
        "",
        "## Goal for the next take",
        "",
        _next_take_goal(weakest, strongest),
        "",
        "## Current take snapshot",
        "",
        f"- **Take:** `{report.inputs.take_path.name}`",
        f"- **Overall score:** {overall_score:.1f}/100",
        f"- **Analysis confidence:** {report.analysis_confidence.level.title()}",
        f"- **Main focus:** {_metric_label(weakest.name.value)} ({weakest.score:.1f}/100)",
        f"- **Keep stable:** {_metric_label(strongest.name.value)} ({strongest.score:.1f}/100)",
    ]

    lines.extend(report_confidence_warning_lines(report))

    if report.summary:
        lines.extend(["", "## Summary", "", report.summary])

    lines.extend(["", "## Keep", ""])
    if report.top_strengths:
        for strength in report.top_strengths:
            lines.append(f"- {strength}")
    else:
        lines.append(f"- Preserve {_metric_label(strongest.name.value)} while working on the main focus area.")

    lines.extend(["", "## Improve", ""])
    if report.top_weaknesses:
        for weakness in report.top_weaknesses:
            lines.append(f"- {weakness}")
    else:
        lines.append(f"- Focus on {_metric_label(weakest.name.value)} before changing everything else.")

    lines.extend(["", "## Practice loops", ""])
    if report.practice_loops:
        for index, loop in enumerate(report.practice_loops, start=1):
            lines.extend([
                f"### Loop {index}: Section {loop.section_index}",
                "",
                f"- **Span:** {loop.start_s:.2f}s - {loop.end_s:.2f}s",
                f"- **Focus:** {_metric_label(loop.focus.value)}",
                f"- **Instruction:** {loop.instruction}",
                "- **Suggested reps:** 5 slow repetitions, then 3 reference-speed repetitions.",
                "",
            ])
    else:
        lines.append("No focused loops were generated. Run one clean full-take pass and compare again.")

    lines.extend(["", "## Next recording target", ""])
    if report.next_practice_step:
        lines.append(report.next_practice_step.removeprefix("Next practice step: "))
    else:
        lines.append(_next_take_goal(weakest, strongest))

    lines.extend(["", "## Confidence notes", ""])
    if report.analysis_confidence.reasons:
        lines.append("Reasons:")
        for reason in report.analysis_confidence.reasons:
            lines.append(f"- {reason}")
    if report.analysis_confidence.limitations:
        lines.append("")
        lines.append("Limitations:")
        for limitation in report.analysis_confidence.limitations:
            lines.append(f"- {limitation}")

    return "\n".join(lines).rstrip() + "\n"


def _next_take_goal(weakest: ComponentScore, strongest: ComponentScore) -> str:
    if weakest.name == strongest.name:
        return f"Record one new take focused on improving {_metric_label(weakest.name.value)}."
    return f"Improve {_metric_label(weakest.name.value)} while preserving {_metric_label(strongest.name.value)}."


def _metric_label(raw_name: str) -> str:
    return raw_name.replace("_", " ").title()
