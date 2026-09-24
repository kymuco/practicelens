from __future__ import annotations

import hashlib
import json
import wave
from pathlib import Path

from practicelens.measurement import InterventionRole
from practicelens.measurement.controlled_perturbations import (
    CONTROLLED_PERTURBATION_GENERATOR_VERSION,
    CONTROLLED_PERTURBATION_SCHEMA_VERSION,
    generate_controlled_perturbation_harness,
)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_controlled_harness_generates_four_ordered_families(tmp_path: Path) -> None:
    result = generate_controlled_perturbation_harness(tmp_path / "controlled")

    by_family: dict[str, list] = {}
    for case in result.cases:
        by_family.setdefault(case.condition.intervention.family, []).append(case)

    assert set(by_family) == {
        "amplitude_gain",
        "broadband_noise",
        "pitch_drift",
        "local_timing_warp",
    }

    for cases in by_family.values():
        strengths = [case.condition.intervention.strength for case in cases]
        assert strengths == sorted(strengths)
        assert strengths[0] == 0.0
        assert cases[0].condition.intervention.role is InterventionRole.CONTROL
        assert all(
            case.condition.intervention.role is not InterventionRole.CONTROL
            for case in cases[1:]
        )


def test_zero_controls_are_byte_identical_to_reference(tmp_path: Path) -> None:
    result = generate_controlled_perturbation_harness(tmp_path / "controlled")

    controls = [
        case
        for case in result.cases
        if case.condition.intervention.role is InterventionRole.CONTROL
    ]

    assert len(controls) == 4
    assert all(case.sha256 == result.reference_sha256 for case in controls)
    assert all(_digest(case.path) == result.reference_sha256 for case in controls)


def test_nonzero_conditions_preserve_wav_shape(tmp_path: Path) -> None:
    result = generate_controlled_perturbation_harness(tmp_path / "controlled")

    with wave.open(str(result.reference_path), "rb") as reference_wav:
        reference_shape = (
            reference_wav.getnchannels(),
            reference_wav.getsampwidth(),
            reference_wav.getframerate(),
            reference_wav.getnframes(),
        )

    for case in result.cases:
        with wave.open(str(case.path), "rb") as case_wav:
            case_shape = (
                case_wav.getnchannels(),
                case_wav.getsampwidth(),
                case_wav.getframerate(),
                case_wav.getnframes(),
            )
        assert case_shape == reference_shape


def test_nonzero_perturbations_change_audio_bytes(tmp_path: Path) -> None:
    result = generate_controlled_perturbation_harness(tmp_path / "controlled")

    changed = [
        case
        for case in result.cases
        if case.condition.intervention.role is not InterventionRole.CONTROL
    ]

    assert changed
    assert all(case.sha256 != result.reference_sha256 for case in changed)


def test_manifest_is_machine_readable_and_preserves_intervention_metadata(
    tmp_path: Path,
) -> None:
    result = generate_controlled_perturbation_harness(tmp_path / "controlled")
    payload = json.loads(result.manifest_path.read_text(encoding="utf-8"))

    assert payload["kind"] == "controlled_perturbation_manifest"
    assert payload["schema_version"] == CONTROLLED_PERTURBATION_SCHEMA_VERSION
    assert payload["generator_version"] == CONTROLLED_PERTURBATION_GENERATOR_VERSION
    assert payload["sample_rate"] == 16_000
    assert payload["reference"]["sha256"] == result.reference_sha256
    assert len(payload["cases"]) == len(result.cases)

    pitch_cases = [
        case
        for case in payload["cases"]
        if case["condition"]["intervention"]["family"] == "pitch_drift"
    ]
    assert [case["condition"]["intervention"]["strength"] for case in pitch_cases] == [
        0.0,
        0.01,
        0.03,
        0.06,
    ]
    assert [case["condition"]["intervention"]["role"] for case in pitch_cases] == [
        "control",
        "target",
        "target",
        "target",
    ]


def test_harness_generation_is_deterministic_across_directories(tmp_path: Path) -> None:
    first = generate_controlled_perturbation_harness(tmp_path / "first")
    second = generate_controlled_perturbation_harness(tmp_path / "second")

    assert first.reference_sha256 == second.reference_sha256

    first_by_id = {case.condition.condition_id: case.sha256 for case in first.cases}
    second_by_id = {case.condition.condition_id: case.sha256 for case in second.cases}
    assert first_by_id == second_by_id
