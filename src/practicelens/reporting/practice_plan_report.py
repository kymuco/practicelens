from __future__ import annotations

from practicelens.domain.models import AnalysisReport, ComponentScore
from practicelens.reporting.markdown_warnings import report_confidence_warning_lines


def report_to_practice_plan_markdown(report: AnalysisReport) -> str:
    """Render a focused practice plan for one analysis report."""

    overall_score = sum(score.score * score.weight for score in report.scores)
    weakest = min(report.scores, key=lambda score: score.score)
    strongest = max(report.scores, key=lambda score: score.score)
    next_recording_target = _next_recording_target(report, weakest, strongest)

    lines: list[str] = [
        "# PracticeLens Practice Plan",
        "",
        "## Goal for the next take",
        "",
        next_recording_target,
        "",
        f"- **Fix first:** {_metric_label(weakest.name.value)} ({weakest.score:.1f}/100)",
        f"- **Keep:** {_metric_label(strongest.name.value)} ({strongest.score:.1f}/100)",
        f"- **Current take:** `{report.inputs.take_path.name}`",
        f"- **Overall score:** {overall_score:.1f}/100",
        f"- **Confidence:** {report.analysis_confidence.level.title()}",
    ]

    lines.extend(_before_next_take_lines(report, weakest, next_recording_target))
    lines.extend(report_confidence_warning_lines(report))

    if report.summary:
        lines.extend(["", "## Summary", "", report.summary])

    lines.extend(["", "## What to keep", ""])
    if report.top_strengths:
        for strength in report.top_strengths:
            lines.append(f"- {strength}")
    else:
        lines.append(f"- Preserve {_metric_label(strongest.name.value)} while working on the main focus area.")

    lines.extend(["", "## What to fix first", ""])
    if report.top_weaknesses:
        for weakness in report.top_weaknesses:
            lines.append(f"- {weakness}")
    else:
        lines.append(f"- Focus on {_metric_label(weakest.name.value)} before changing everything else.")

    lines.extend(["", "## Why this matters", "", _why_this_matters(weakest, strongest)])

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

    lines.extend(["", "## Next recording target", "", next_recording_target])

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


def _before_next_take_lines(report: AnalysisReport, weakest: ComponentScore, next_recording_target: str) -> list[str]:
    lines = ["", "## Before next take", ""]
    if report.practice_loops:
        loop = report.practice_loops[0]
        lines.append(
            f"1. Loop Section {loop.section_index} ({loop.start_s:.2f}s - {loop.end_s:.2f}s) "
            f"and focus on {_metric_label(loop.focus.value)}."
        )
    else:
        lines.append("1. Run one clean full-take pass before section-level loop work.")

    lines.extend([
        f"2. Keep attention on {_metric_label(weakest.name.value)} before changing anything else.",
        f"3. Record one clean complete attempt: {next_recording_target}",
    ])
    return lines


def _next_recording_target(report: AnalysisReport, weakest: ComponentScore, strongest: ComponentScore) -> str:
    if report.next_practice_step:
        return report.next_practice_step.removeprefix("Next practice step: ")
    return _next_take_goal(weakest, strongest)


def _next_take_goal(weakest: ComponentScore, strongest: ComponentScore) -> str:
    if weakest.name == strongest.name:
        return f"Record one new take focused on improving {_metric_label(weakest.name.value)}."
    return (
        f"Record one new take focused on improving {_metric_label(weakest.name.value)} "
        f"while preserving {_metric_label(strongest.name.value)}."
    )


def _why_this_matters(weakest: ComponentScore, strongest: ComponentScore) -> str:
    weakest_label = _metric_label(weakest.name.value)
    strongest_label = _metric_label(strongest.name.value)
    if weakest.name == strongest.name:
        return f"{weakest_label} is the main area to stabilize before broadening the practice target."
    return (
        f"{weakest_label} is the lowest-scoring area right now. Work on it first while protecting "
        f"{strongest_label}, so the next take improves without losing what is already stable."
    )


def _metric_label(raw_name: str) -> str:
    return raw_name.replace("_", " ").title()
