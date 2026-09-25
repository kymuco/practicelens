from __future__ import annotations

from pathlib import Path

import pytest

from practicelens.domain.models import AnalysisConfig
from practicelens.measurement.baseline_audit import AUDITED_MEASUREMENTS
from practicelens.measurement.local_session_repeatability import (
    LocalSessionTakeObservation,
    _measurement_repeatability_stats,
    _validate_local_repeatability_sources,
    local_session_repeatability_payload,
)


def _observation(index: int, values: tuple[float, float, float, float]) -> LocalSessionTakeObservation:
    return LocalSessionTakeObservation(
        take_id=f"take_{index:02d}",
        measurements=dict(zip(AUDITED_MEASUREMENTS, values, strict=True)),
        confidence_level="high",
        suitability_status="ok",
        alignment_coverage=1.0,
    )


def test_repeatability_stats_report_robust_and_conservative_spread() -> None:
    stats = _measurement_repeatability_stats([90.0, 91.0, 92.0, 93.0, 110.0])

    assert stats == {
        "median": 92.0,
        "minimum": 90.0,
        "maximum": 110.0,
        "observed_span": 20.0,
        "median_abs_deviation": 1.0,
        "max_abs_deviation_from_median": 18.0,
        "median_pairwise_abs_delta": 2.5,
        "max_pairwise_abs_delta": 20.0,
    }


def test_payload_contains_no_source_paths_or_fingerprints() -> None:
    observations = tuple(
        _observation(
            index,
            (
                90.0 + index,
                80.0 + index * 0.5,
                85.0 - index * 0.25,
                88.0 + index * 0.1,
            ),
        )
        for index in range(1, 6)
    )

    payload = local_session_repeatability_payload(
        observations,
        session_label="same-session-a",
        code_revision="abc123",
        config=AnalysisConfig(),
    )

    assert payload["kind"] == "local_session_repeatability"
    assert payload["take_count"] == 5
    assert payload["privacy"] == {
        "audio_embedded": False,
        "source_paths_embedded": False,
        "source_fingerprints_embedded": False,
    }

    serialized = str(payload)
    assert ".wav" not in serialized
    assert "/" not in serialized
    assert "\\" not in serialized


def test_payload_surfaces_quality_flags_without_dropping_takes() -> None:
    observations = (
        _observation(1, (90.0, 90.0, 90.0, 90.0)),
        _observation(2, (91.0, 91.0, 91.0, 91.0)),
        _observation(3, (92.0, 92.0, 92.0, 92.0)),
        LocalSessionTakeObservation(
            take_id="take_04",
            measurements={name: 93.0 for name in AUDITED_MEASUREMENTS},
            confidence_level="low",
            suitability_status="review",
            alignment_coverage=0.7,
        ),
        _observation(5, (94.0, 94.0, 94.0, 94.0)),
    )

    payload = local_session_repeatability_payload(
        observations,
        session_label=None,
        code_revision=None,
        config=AnalysisConfig(),
    )

    assert payload["take_count"] == 5
    assert payload["quality_summary"]["flags"] == [
        "non_ok_input_suitability_present",
        "low_analysis_confidence_present",
        "alignment_coverage_below_0_85",
    ]


def test_payload_rejects_too_few_takes() -> None:
    observations = tuple(
        _observation(index, (90.0, 90.0, 90.0, 90.0))
        for index in range(1, 5)
    )

    with pytest.raises(ValueError, match="at least 5 independent takes"):
        local_session_repeatability_payload(
            observations,
            session_label=None,
            code_revision=None,
            config=AnalysisConfig(),
        )


def test_source_validation_rejects_duplicate_takes(tmp_path: Path) -> None:
    reference = tmp_path / "reference.wav"
    reference.write_bytes(b"reference")
    takes = []
    for index in range(5):
        path = tmp_path / f"take_{index}.wav"
        path.write_bytes(b"duplicate" if index in {1, 4} else f"take-{index}".encode())
        takes.append(path)

    with pytest.raises(ValueError, match="duplicates take 2"):
        _validate_local_repeatability_sources(reference, tuple(takes))


def test_source_validation_rejects_reference_reused_as_take(tmp_path: Path) -> None:
    reference = tmp_path / "reference.wav"
    reference.write_bytes(b"same")
    takes = []
    for index in range(5):
        path = tmp_path / f"take_{index}.wav"
        path.write_bytes(b"same" if index == 2 else f"take-{index}".encode())
        takes.append(path)

    with pytest.raises(ValueError, match="byte-identical to the reference"):
        _validate_local_repeatability_sources(reference, tuple(takes))
