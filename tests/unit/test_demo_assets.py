import json
import wave
from pathlib import Path

from practicelens.demo_assets import generate_demo_assets


def test_generate_demo_assets_writes_expected_demo_files(tmp_path: Path) -> None:
    paths = generate_demo_assets(tmp_path)

    assert set(paths) == {"reference", "take", "take_01", "take_02", "take_03", "manifest"}
    assert paths["manifest"].exists()

    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    assert manifest["sample_rate"] == 16_000
    assert manifest["duration_samples"] == 8_000
    assert set(manifest["assets"]) == {"reference", "take", "take_01", "take_02", "take_03"}

    for key in ("reference", "take", "take_01", "take_02", "take_03"):
        path = paths[key]
        assert path.exists()
        with wave.open(str(path), "rb") as wav_file:
            assert wav_file.getnchannels() == 1
            assert wav_file.getsampwidth() == 2
            assert wav_file.getframerate() == 16_000
            assert wav_file.getnframes() == 8_000
