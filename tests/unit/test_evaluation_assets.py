from __future__ import annotations

import json
import wave
from pathlib import Path

from practicelens.evaluation_assets import CASE_SPECS, REFERENCE_CASE, generate_evaluation_assets


def test_generate_evaluation_assets_writes_manifest_and_wavs(tmp_path: Path) -> None:
    generated = generate_evaluation_assets(tmp_path)

    assert set(generated) == {spec.name for spec in CASE_SPECS} | {"manifest"}
    assert generated[REFERENCE_CASE].name == "reference_phrase.wav"
    assert generated["manifest"].exists()

    manifest = json.loads(generated["manifest"].read_text(encoding="utf-8"))
    assert manifest["schema_version"] == 1
    assert manifest["reference_case"] == REFERENCE_CASE
    assert len(manifest["cases"]) == len(CASE_SPECS)

    for spec in CASE_SPECS:
        path = generated[spec.name]
        assert path.exists()
        with wave.open(str(path), "rb") as wav_file:
            assert wav_file.getnchannels() == 1
            assert wav_file.getsampwidth() == 2
            assert wav_file.getframerate() == 16_000
            assert wav_file.getnframes() > 0


def test_generate_evaluation_assets_is_deterministic(tmp_path: Path) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    first = generate_evaluation_assets(first_dir)
    second = generate_evaluation_assets(second_dir)

    for spec in CASE_SPECS:
        assert first[spec.name].read_bytes() == second[spec.name].read_bytes()

    first_manifest = json.loads(first["manifest"].read_text(encoding="utf-8"))
    second_manifest = json.loads(second["manifest"].read_text(encoding="utf-8"))
    for manifest in (first_manifest, second_manifest):
        for case in manifest["cases"]:
            case.pop("path")
    assert first_manifest == second_manifest


def test_evaluation_manifest_describes_expected_case_roles(tmp_path: Path) -> None:
    generated = generate_evaluation_assets(tmp_path)
    manifest = json.loads(generated["manifest"].read_text(encoding="utf-8"))

    cases = {case["name"]: case for case in manifest["cases"]}
    assert cases[REFERENCE_CASE]["role"] == "reference"
    assert cases["pitch_drift_take"]["expected_weakness"] == "pitch_fidelity"
    assert cases["timing_drift_take"]["expected_weakness"] == "timing_consistency"
    assert cases["rhythm_mistake_take"]["expected_weakness"] == "rhythm_fidelity"
