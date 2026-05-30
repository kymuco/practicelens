from __future__ import annotations

from practicelens.domain.models import InputSuitabilitySummary


def input_suitability_to_payload(summary: InputSuitabilitySummary) -> dict[str, object]:
    return {
        "schema_version": int(summary.schema_version),
        "status": summary.status,
        "reference_duration_s": summary.reference_duration_s,
        "take_duration_s": summary.take_duration_s,
        "duration_ratio": summary.duration_ratio,
        "alignment_coverage": summary.alignment_coverage,
        "voiced_frame_coverage": summary.voiced_frame_coverage,
        "reference_voiced_frame_coverage": summary.reference_voiced_frame_coverage,
        "take_voiced_frame_coverage": summary.take_voiced_frame_coverage,
        "onset_evidence": summary.onset_evidence,
        "reference_onset_count": summary.reference_onset_count,
        "take_onset_count": summary.take_onset_count,
        "reasons": list(summary.reasons),
    }
