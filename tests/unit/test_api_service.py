import math
import wave
from pathlib import Path

import pytest

from practicelens.api import analyze_payload, build_request_from_payload


def _write_wav(path: Path, samples: list[float], *, sample_rate: int = 16_000) -> None:
    ints = [max(-32767, min(32767, int(sample * 32767))) for sample in samples]
    frames = bytearray()
    for value in ints:
        frames.extend(int(value).to_bytes(2, byteorder="little", signed=True))
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(bytes(frames))


def test_build_request_from_payload_maps_api_fields() -> None:
    request = build_request_from_payload(
        {
            "reference_path": "reference.wav",
            "take_path": "take.wav",
            "out_dir": "out",
            "sample_rate": 22_050,
            "frame_length": 1024,
            "hop_length": 256,
            "segment_duration": 3.5,
        }
    )

    assert request.reference_path == Path("reference.wav")
    assert request.take_path == Path("take.wav")
    assert request.out_dir == Path("out")
    assert request.config.target_sample_rate == 22_050
    assert request.config.frame_length == 1024
    assert request.config.hop_length == 256
    assert request.config.segment_duration_s == 3.5


def test_build_request_from_payload_rejects_missing_paths() -> None:
    with pytest.raises(ValueError):
        build_request_from_payload({"take_path": "take.wav"})


def test_analyze_payload_returns_json_ready_report(tmp_path: Path) -> None:
    reference = tmp_path / "reference.wav"
    take = tmp_path / "take.wav"
    out_dir = tmp_path / "api-out"

    reference_samples = [math.sin(2.0 * math.pi * 220.0 * index / 16_000.0) for index in range(8000)]
    take_samples = [math.sin(2.0 * math.pi * 220.0 * index / 16_000.0) for index in range(8000)]
    _write_wav(reference, reference_samples)
    _write_wav(take, take_samples)

    payload = analyze_payload(
        {
            "reference_path": str(reference),
            "take_path": str(take),
            "out_dir": str(out_dir),
            "frame_length": 1024,
            "hop_length": 256,
            "segment_duration": 2.0,
        }
    )

    assert payload["overview"]["ok"] is True
    assert payload["inputs"]["reference_path"] == str(reference)
    assert payload["scores"]
    assert (out_dir / "report.json").exists()
    assert (out_dir / "report.md").exists()
