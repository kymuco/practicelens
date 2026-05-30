from __future__ import annotations

from practicelens.application.contracts import BatchCompareResult, BatchSessionSummary, SessionPracticeLoopSummary
from practicelens.reporting.markdown_warnings import batch_confidence_warning_lines


def batch_compare_result_to_practice_plan_markdown(result: BatchCompareResult) -> str:
    """Render a session-level practice plan for one batch comparison."""

    if result.session_summary is None:
        raise ValueError("batch practice plan requires a session_summary")

    summary = result.session_summary
    lines: list[str] = [
        "# PracticeLens Batch Practice Plan",
        "",
        "## Session goal",
        "",
        summary.next_recording_target,
        "",
        "## Keep take",
        "",
        f"- **Best take:** `{summary.best_take.take_path.name}`",
        f"- **Best score:** {summary.best_take.overall_score:.1f}/100",
    ]
    if result.best_entry.summary:
        lines.append(f"- **Why:** {result.best_entry.summary}")

    lines.extend(batch_confidence_warning_lines(result))

    lines.extend([
        "",
        "## Recurring weakness across takes",
        "",
        f"- **Primary recurring weakness:** {_metric_label(summary.recurring_weakness.value)}",
        _weakness_support_line(summary),
        "",
        "## Strongest stable area",
        "",
        f"- **Stable strength:** {_metric_label(summary.strongest_stable_area.value)}",
        f"- Average score across takes: {summary.strongest_stable_area_average_score:.1f}/100.",
        "",
        "## Top practice loops",
        "",
    ])

    if summary.practice_loops:
        for index, loop in enumerate(summary.practice_loops, start=1):
            lines.extend(_practice_loop_lines(index, loop))
    else:
        lines.append("No focused loops were generated across the compared takes.")

    lines.extend([
        "",
        "## Next recording target",
        "",
        summary.next_recording_target,
        "",
        "## Take ranking snapshot",
        "",
        "| Rank | Take | Score |",
        "| --- | --- | ---: |",
    ])
    for entry in result.entries:
        lines.append(f"| {entry.rank} | `{entry.take_path.name}` | {entry.overall_score:.1f} |")

    return "\n".join(lines).rstrip() + "\n"


def _weakness_support_line(summary: BatchSessionSummary) -> str:
    return (
        f"- Appears as the weakest area in {summary.recurring_weakness_count} "
        f"of {summary.compared_takes} compared takes."
    )


def _practice_loop_lines(index: int, loop: SessionPracticeLoopSummary) -> list[str]:
    return [
        f"### Loop {index}: `{loop.take_path.name}` Section {loop.section_index}",
        "",
        f"- **Take rank:** #{loop.take_rank}",
        f"- **Span:** {loop.start_s:.2f}s - {loop.end_s:.2f}s",
        f"- **Focus:** {_metric_label(loop.focus.value)}",
        f"- **Instruction:** {loop.instruction}",
        "",
    ]


def _metric_label(raw_name: str) -> str:
    return raw_name.replace("_", " ").title()
