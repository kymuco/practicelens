from __future__ import annotations

from practicelens.application.contracts import BatchCompareResult
from practicelens.domain.models import AnalysisReport, InputSuitabilitySummary


def report_confidence_warning_lines(report: AnalysisReport, *, heading: str = "## Recording Confidence Warnings") -> list[str]:
    """Render concise, action-oriented Markdown warnings for one analysis report."""

    warnings = _report_warning_items(report)
    if not warnings:
        return []

    actions = _report_action_items(report.input_suitability)
    lines = [
        "",
        heading,
        "",
        "PracticeLens can still render this report, but review detailed feedback cautiously before acting on it.",
        "",
        "Warnings:",
    ]
    lines.extend(f"- {warning}" for warning in warnings)
    lines.extend(["", "How to improve the next recording:"])
    lines.extend(f"- {action}" for action in actions)
    return lines


def batch_confidence_warning_lines(result: BatchCompareResult, *, heading: str = "## Recording Confidence Warnings") -> list[str]:
    """Render a compact batch-level Markdown warning section."""

    warning_entries = [entry for entry in result.entries if _report_warning_items(entry.result.report)]
    if not warning_entries:
        return []

    lines = [
        "",
        heading,
        "",
        "Some takes have lower input confidence. Review rankings cautiously until the recordings are cleaner.",
        "",
        "Affected takes:",
    ]
    for entry in warning_entries:
        report = entry.result.report
        first_warning = _report_warning_items(report)[0]
        lines.append(f"- `#{entry.rank} {entry.take_path.name}`: {first_warning}")

    actions = _dedupe_action_items(
        action
        for entry in warning_entries
        for action in _report_action_items(entry.result.report.input_suitability)
    )
    lines.extend(["", "How to improve the next recording:"])
    lines.extend(f"- {action}" for action in actions)
    return lines


def _report_warning_items(report: AnalysisReport) -> list[str]:
    warnings: list[str] = []
    confidence_level = report.analysis_confidence.level.lower()
    if confidence_level != "high":
        reason = report.analysis_confidence.reasons[0] if report.analysis_confidence.reasons else "evidence is limited."
        warnings.append(f"Analysis confidence is {confidence_level}; {reason}")

    suitability = report.input_suitability
    if suitability.status != "ok":
        warnings.append(f"Input suitability is {suitability.status.replace('_', ' ')}.")

    if suitability.duration_diagnostic not in {"duration_ratio_ok", "duration_ratio_unavailable"}:
        warnings.append(suitability.duration_diagnostic_message or "Take duration may not match the reference.")
    if suitability.start_diagnostic not in {"start_region_ok", "start_region_unavailable"}:
        warnings.append(suitability.start_diagnostic_message or "The take start may not align cleanly with the reference.")
    if suitability.alignment_coverage < 0.85:
        warnings.append(f"Alignment coverage is limited ({suitability.alignment_coverage:.2f}).")
    if suitability.voiced_frame_coverage < 0.35:
        warnings.append(f"Voiced-frame coverage is limited ({suitability.voiced_frame_coverage:.2f}).")
    if suitability.onset_evidence != "present":
        warnings.append(f"Onset evidence is {suitability.onset_evidence}.")

    return _dedupe_action_items(warnings)


def _report_action_items(suitability: InputSuitabilitySummary) -> list[str]:
    actions: list[str] = []
    if suitability.duration_diagnostic != "duration_ratio_ok":
        actions.append("Record the same musical section as the reference and trim obvious leading or trailing silence.")
    if suitability.start_diagnostic == "take_activity_starts_late":
        actions.append("Use a short count-in, then start the first note clearly and close to the reference start.")
    elif suitability.start_diagnostic == "take_leading_noise_before_activity":
        actions.append("Pause before playing and reduce handling, pickup, breath, or room noise before the first note.")
    if suitability.alignment_coverage < 0.85:
        actions.append("Record a complete take with fewer stops, restarts, or unrelated sections.")
    if suitability.voiced_frame_coverage < 0.35:
        actions.append("Make the main notes clearer and loud enough for stable pitch or voiced-frame detection.")
    if suitability.onset_evidence != "present":
        actions.append("Play the first attacks clearly so onset evidence is easier to detect.")
    if not actions:
        actions.append("Record one cleaner full take before relying on detailed section feedback.")
    return _dedupe_action_items(actions)


def _dedupe_action_items(items: list[str] | object) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in items:
        if not isinstance(item, str):
            continue
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped
