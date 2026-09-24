from __future__ import annotations

from pathlib import Path

import pytest

from practicelens.domain.models import AnalysisConfig
from practicelens.measurement.baseline_audit import AUDITED_MEASUREMENTS
from practicelens.measurement.equivalence_floor import (
    EquivalentRecordingCase,
    generate_equivalent_recording_cases,
    synthetic_equivalence_floor_payload,
)


def test_equivalence_generator_covers_only_semantics_preserving_families(
    tmp_path: Path,
) -> None:
    reference_path, cases = generate_equivalent_recording_cases(tmp_path / "eq")

    assert reference_path.is_file()
    assert len(cases) == 11
    assert {case.family for case in cases} == {
        "exact_copy",
        "pcm_roundtrip",
        "polarity",
        "gain",
        "dc_offset",
        "recording_window",
    }
    assert all(case.path.is_file() for case in cases)


def test_exact_byte_copy_preserves_reference_digest(tmp_path: Path) -> None:
    reference_path, cases = generate_equivalent_recording_cases(tmp_path / "eq")

    copied = next(case for case in cases if case.case_id == "exact_byte_copy")

    import hashlib

    reference_digest = hashlib.sha256(reference_path.read_bytes()).hexdigest()
    assert copied.sha256 == reference_digest


def test_floor_payload_uses_max_absolute_equivalence_delta() -> None:
    baseline = {name: 100.0 for name in AUDITED_MEASUREMENTS}
    repeat_values = (
        dict(baseline),
        {
            **baseline,
            "pitch_fidelity": 99.9,
        },
    )
    cases = (
        EquivalentRecordingCase(
            case_id="a",
            family="polarity",
            path=Path("a.wav"),
            sha256="a" * 64,
        ),
        EquivalentRecordingCase(
            case_id="b",
            family="recording_window",
            path=Path("b.wav"),
            sha256="b" * 64,
        ),
    )
    case_values = {
        "a": {
            "pitch_fidelity": 99.5,
            "rhythm_fidelity": 100.0,
            "timing_consistency": 99.8,
            "section_stability": 99.9,
        },
        "b": {
            "pitch_fidelity": 99.8,
            "rhythm_fidelity": 99.7,
            "timing_consistency": 99.0,
            "section_stability": 99.5,
        },
    }
    case_deltas = {
        case_id: {
            name: values[name] - baseline[name]
            for name in AUDITED_MEASUREMENTS
        }
        for case_id, values in case_values.items()
    }

    payload = synthetic_equivalence_floor_payload(
        baseline=baseline,
        repeat_values=repeat_values,
        cases=cases,
        case_values=case_values,
        case_deltas=case_deltas,
        code_revision="test",
        config=AnalysisConfig(),
    )

    assert payload["exact_repeat_floor"]["pitch_fidelity"] == pytest.approx(0.1)
    assert payload["tested_equivalence_floor"] == pytest.approx(
        {
            "pitch_fidelity": 0.5,
            "rhythm_fidelity": 0.3,
            "timing_consistency": 1.0,
            "section_stability": 0.5,
        }
    )
    assert payload["tested_equivalence_floor_source"] == {
        "pitch_fidelity": "a",
        "rhythm_fidelity": "b",
        "timing_consistency": "b",
        "section_stability": "b",
    }
