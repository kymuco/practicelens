from __future__ import annotations

from collections import Counter, defaultdict

from practicelens.application.contracts import BatchCompareEntry, BatchCompareResult
from practicelens.domain.enums import MetricName
from practicelens.domain.models import ComponentScore, PracticeLoop


def batch_compare_result_to_practice_plan_markdown(result: BatchCompareResult) -> str:
    """Render a session-level practice plan for one batch comparison."""

    best = result.best_entry
    recurring_weakness = _recurring_weakness(result.entries)
    stable_strength = _stable_strength(result.entries)
    recommended_loops = _recommended_loops(result.entries)

    lines: list[str] = [
        "# PracticeLens Batch Practice Plan",
        "",
        "## Session goal",
        "",
        _next_recording_target(recurring_weakness, stable_strength),
        "",
        "## Keep take",
        "",
        f"- **Best take:** `{best.take_path.name}`",
        f"- **Best score:** {best.overall_score:.1f}/100",
    ]
    if best.summary:
        lines.append(f"- **Why:** {best.summary}")

    lines.extend([
        "",
        "## Recurring weakness across takes",
        "",
        f"- **Primary recurring weakness:** {_metric_label(recurring_weakness.value)}",
        _weakness_support_line(result.entries, recurring_weakness),
        "",
        "## Strongest stable area",
        "",
        f"- **Stable strength:** {_metric_label(stable_strength.value)}",
        _strength_support_line(result.entries, stable_strength),
        "",
        "## Top practice loops",
        "",
    ])

    if recommended_loops:
        for index, item in enumerate(recommended_loops, start=1):
            entry, loop = item
            lines.extend([
                f"### Loop {index}: `{entry.take_path.name}` Section {loop.section_index}",
                "",
                f"- **Take rank:** #{entry.rank}",
                f"- **Take score:** {entry.overall_score:.1f}/100",
                f"- **Span:** {loop.start_s:.2f}s - {loop.end_s:.2f}s",
                f"- **Focus:** {_metric_label(loop.focus.value)}",
                f"- **Instruction:** {loop.instruction}",
                "",
            ])
    else:
        lines.append("No focused loops were generated across the compared takes.")

    lines.extend([
        "",
        "## Next recording target",
        "",
        _next_recording_target(recurring_weakness, stable_strength),
        "",
        "## Take ranking snapshot",
        "",
        "| Rank | Take | Score | Main weakness | Strongest area |",
        "| --- | --- | ---: | --- | --- |",
    ])
    for entry in result.entries:
        weakness = _weakest_metric(entry)
        strength = _strongest_metric(entry)
        lines.append(
            f"| {entry.rank} | `{entry.take_path.name}` | {entry.overall_score:.1f} | "
            f"{_metric_label(weakness.value)} | {_metric_label(strength.value)} |"
        )

    return "\n".join(lines).rstrip() + "\n"


def _recurring_weakness(entries: tuple[BatchCompareEntry, ...]) -> MetricName:
    counts: Counter[MetricName] = Counter(_weakest_metric(entry) for entry in entries)
    average_scores = _average_metric_scores(entries)
    return min(counts, key=lambda name: (-counts[name], average_scores[name], name.value))


def _stable_strength(entries: tuple[BatchCompareEntry, ...]) -> MetricName:
    average_scores = _average_metric_scores(entries)
    return max(average_scores, key=lambda name: (average_scores[name], name.value))


def _recommended_loops(
    entries: tuple[BatchCompareEntry, ...],
    *,
    limit: int = 3,
) -> tuple[tuple[BatchCompareEntry, PracticeLoop], ...]:
    candidates: list[tuple[float, int, int, BatchCompareEntry, PracticeLoop]] = []
    for entry in sorted(entries, key=lambda item: (item.overall_score, item.rank)):
        for loop_index, loop in enumerate(entry.result.report.practice_loops):
            candidates.append((entry.overall_score, entry.rank, loop_index, entry, loop))
    return tuple((entry, loop) for _, _, _, entry, loop in candidates[:limit])


def _weakest_metric(entry: BatchCompareEntry) -> MetricName:
    scores = _report_scores(entry)
    return min(scores, key=lambda score: (score.score, score.name.value)).name


def _strongest_metric(entry: BatchCompareEntry) -> MetricName:
    scores = _report_scores(entry)
    return max(scores, key=lambda score: (score.score, score.name.value)).name


def _average_metric_scores(entries: tuple[BatchCompareEntry, ...]) -> dict[MetricName, float]:
    values: dict[MetricName, list[float]] = defaultdict(list)
    for entry in entries:
        for score in _report_scores(entry):
            values[score.name].append(score.score)
    return {name: sum(scores) / len(scores) for name, scores in values.items() if scores}


def _report_scores(entry: BatchCompareEntry) -> tuple[ComponentScore, ...]:
    return entry.result.report.scores


def _weakness_support_line(entries: tuple[BatchCompareEntry, ...], metric: MetricName) -> str:
    count = sum(1 for entry in entries if _weakest_metric(entry) == metric)
    return f"- Appears as the weakest area in {count} of {len(entries)} compared takes."


def _strength_support_line(entries: tuple[BatchCompareEntry, ...], metric: MetricName) -> str:
    average_scores = _average_metric_scores(entries)
    return f"- Average score across takes: {average_scores[metric]:.1f}/100."


def _next_recording_target(recurring_weakness: MetricName, stable_strength: MetricName) -> str:
    if recurring_weakness == stable_strength:
        return f"Record one new take focused on improving {_metric_label(recurring_weakness.value)}."
    return (
        f"Record one new take that improves {_metric_label(recurring_weakness.value)} "
        f"while preserving {_metric_label(stable_strength.value)}."
    )


def _metric_label(raw_name: str) -> str:
    return raw_name.replace("_", " ").title()
