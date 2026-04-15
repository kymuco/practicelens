from __future__ import annotations

import json
import math
import wave
from pathlib import Path

DEFAULT_SAMPLE_RATE = 16_000
DEFAULT_DURATION_SAMPLES = 8_000
DEFAULT_OUT_DIR = Path("examples/demo_assets/generated")


def generate_demo_assets(
    out_dir: Path = DEFAULT_OUT_DIR,
    *,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    duration_samples: int = DEFAULT_DURATION_SAMPLES,
) -> dict[str, Path]:
    """Generate deterministic synthetic WAV assets for demos, onboarding, and smoke tests."""

    out_dir.mkdir(parents=True, exist_ok=True)
    file_specs = {
        "reference": 220.0,
        "take": 220.0,
        "take_01": 261.63,
        "take_02": 220.0,
        "take_03": 233.08,
    }

    paths: dict[str, Path] = {}
    for stem, freq_hz in file_specs.items():
        path = out_dir / f"{stem}.wav"
        _write_wav(path, _sine_samples(freq_hz, sample_rate=sample_rate, duration_samples=duration_samples), sample_rate=sample_rate)
        paths[stem] = path

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "sample_rate": sample_rate,
                "duration_samples": duration_samples,
                "assets": {
                    name: {
                        "path": str(path),
                        "role": _role_for_asset(name),
                    }
                    for name, path in paths.items()
                },
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    paths["manifest"] = manifest_path
    return paths


def _role_for_asset(name: str) -> str:
    if name == "reference":
        return "Reference WAV used by both CLI and API demos."
    if name == "take":
        return "Single-analysis demo take."
    if name == "take_02":
        return "Strongest batch-comparison demo take."
    if name == "take_03":
        return "Mid-quality batch-comparison demo take."
    return "Weakest batch-comparison demo take."


def _sine_samples(freq_hz: float, *, sample_rate: int, duration_samples: int) -> list[float]:
    return [math.sin(2.0 * math.pi * freq_hz * index / sample_rate) * 0.8 for index in range(duration_samples)]


def _write_wav(path: Path, samples: list[float], *, sample_rate: int) -> None:
    ints = [max(-32767, min(32767, int(sample * 32767))) for sample in samples]
    frames = bytearray()
    for value in ints:
        frames.extend(int(value).to_bytes(2, byteorder="little", signed=True))
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(bytes(frames))
