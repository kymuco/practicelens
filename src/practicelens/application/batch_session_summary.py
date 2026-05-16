from __future__ import annotations

from collections import Counter, defaultdict

from practicelens.application.contracts import (
    BatchCompareEntry,
    BatchSessionSummary,
    SessionPracticeLoopSummary,
    SessionTakeSummary,
)
from practicelens.domain.enums import MetricName
from practicelens.domain.models import ComponentScore, PracticeLoop


def build_batch_session_summary(entries: tuple[BatchCompareEntry, ...]) -> BatchSessionSummary:
    """Build a stable session-level summary from ranked batch entries."""

    best = entries[0]
    weakest = min(entries, key=lambda entry: (entry.overall_score, entry.rank))
    recurring_weakness, recurring_weakness_count = _recurring_weakness(entries)
    strongest_stable_area, strongest_average_score = _stable_strength(entries)
    return BatchSessionSummary(
        compared_takes=len(entries),
        best_take=_take_summary(best),
        weakest_take=_take_summary(weakest),
        recurring_weakness=recurring_weakness,
        recurring_weakness_count=recurring_weakness_count,
        strongest_stable_area=strongest_stable_area,
        strongest_stable_area_average_score=strongest_average_score,
        next_recording_target=_next_recording_target(recurring_weakness, strongest_stable_area),
        practice_loops=_practice_loop_summaries(entries),
    )


def _take_summary(entry: BatchCompareEntry) -> SessionTakeSummary:
    return SessionTakeSummary(
        rank=entry.rank,
        take_path=entry.take_path,
        overall_score=entry.overall_score,
    )


def _recurring_weakness(entries: tuple[BatchCompareEntry, ...]) -> tuple[MetricName, int]:
    counts: Counter[MetricName] = Counter(_weakest_metric(entry) for entry in entries)
    average_scores = _average_metric_scores(entries)
    weakness = min(counts, key=lambda name: (-counts[name], average_scores[name], name.value))
    return weakness, counts[weakness]


def _stable_strength(entries: tuple[BatchCompareEntry, ...]) -> tuple[MetricName, float]:
    average_scores = _average_metric_scores(entries)
    strength = max(average_scores, key=lambda name: (average_scores[name], name.value))
    return strength, average_scores[strength]


def _practice_loop_summaries(
    entries: tuple[BatchCompareEntry, ...],
    *,
    limit: int = 3,
) -> tuple[SessionPracticeLoopSummary, ...]:
    candidates: list[tuple[float, int, int, BatchCompareEntry, PracticeLoop]] = []
    for entry in sorted(entries, key=lambda item: (item.overall_score, item.rank)):
        for loop_index, loop in enumerate(entry.result.report.practice_loops):
            candidates.append((entry.overall_score, entry.rank, loop_index, entry, loop))
    return tuple(_practice_loop_summary(entry, loop) for _, _, _, entry, loop in candidates[:limit])


def _practice_loop_summary(entry: BatchCompareEntry, loop: PracticeLoop) -> SessionPracticeLoopSummary:
    return SessionPracticeLoopSummary(
        take_rank=entry.rank,
        take_path=entry.take_path,
        section_index=loop.section_index,
        start_s=loop.start_s,
        end_s=loop.end_s,
        focus=loop.focus,
        instruction=loop.instruction,
    )


def _weakest_metric(entry: BatchCompareEntry) -> MetricName:
    scores = _report_scores(entry)
    return min(scores, key=lambda score: (score.score, score.name.value)).name


def _average_metric_scores(entries: tuple[BatchCompareEntry, ...]) -> dict[MetricName, float]:
    values: dict[MetricName, list[float]] = defaultdict(list)
    for entry in entries:
        for score in _report_scores(entry):
            values[score.name].append(score.score)
    return {name: sum(scores) / len(scores) for name, scores in values.items() if scores}


def _report_scores(entry: BatchCompareEntry) -> tuple[ComponentScore, ...]:
    return entry.result.report.scores


def _next_recording_target(recurring_weakness: MetricName, stable_strength: MetricName) -> str:
    if recurring_weakness == stable_strength:
        return f"Record one new take focused on improving {_metric_label(recurring_weakness.value)}."
    return (
        f"Record one new take that improves {_metric_label(recurring_weakness.value)} "
        f"while preserving {_metric_label(stable_strength.value)}."
    )


def _metric_label(raw_name: str) -> str:
    return raw_name.replace("_", " ").title()
