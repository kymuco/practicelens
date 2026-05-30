import json
import math
import wave
from pathlib import Path

import pytest

from practicelens.api import (
    analyze_payload,
    build_batch_request_from_payload,
    build_request_from_payload,
    compare_batch_payload,
    practice_session_payload,
)


def _write_wav(path: Path, freq_hz: float, *, sample_rate: int = 16_000, duration_samples: int = 8000) -> None:
    ints = [
        max(-32767, min(32767, int(math.sin(2.0 * math.pi * freq_hz * index / sample_rate) * 32767)))
        for index in range(duration_samples)
    ]
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


def test_build_batch_request_from_payload_maps_take_list() -> None:
    request = build_batch_request_from_payload(
        {
            "reference_path": "reference.wav",
            "take_paths": ["take_a.wav", "take_b.wav"],
            "out_dir": "batch-out",
            "frame_length": 1024,
            "hop_length": 256,
            "segment_duration": 2.5,
        }
    )

    assert request.reference_path == Path("reference.wav")
    assert request.take_paths == (Path("take_a.wav"), Path("take_b.wav"))
    assert request.out_dir == Path("batch-out")
    assert request.config.frame_length == 1024
    assert request.config.segment_duration_s == 2.5


def test_build_batch_request_from_payload_rejects_missing_take_paths() -> None:
    with pytest.raises(ValueError):
        build_batch_request_from_payload({"reference_path": "reference.wav"})


def test_analyze_payload_returns_contract_shaped_report(tmp_path: Path) -> None:
    reference = tmp_path / "reference.wav"
    take = tmp_path / "take.wav"
    out_dir = tmp_path / "api-out"

    _write_wav(reference, 220.0)
    _write_wav(take, 220.0)

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
    assert isinstance(payload["scores"], list)
    assert isinstance(payload["metrics"], list)
    assert isinstance(payload["sections"], list)
    assert isinstance(payload["artifacts"], list)
    assert payload["input_suitability"]["schema_version"] == 1
    assert payload["input_suitability"]["status"] in {"ok", "warning", "low_confidence"}
    assert payload["input_suitability"]["reference_duration_s"] > 0.0
    assert payload["input_suitability"]["take_duration_s"] > 0.0
    assert (out_dir / "report.json").exists()
    assert (out_dir / "report.md").exists()


def test_compare_batch_payload_returns_ranked_contract_report(tmp_path: Path) -> None:
    reference = tmp_path / "reference.wav"
    take_best = tmp_path / "take_best.wav"
    take_low = tmp_path / "take_low.wav"
    out_dir = tmp_path / "batch-api-out"

    _write_wav(reference, 220.0)
    _write_wav(take_best, 220.0)
    _write_wav(take_low, 261.63)

    payload = compare_batch_payload(
        {
            "reference_path": str(reference),
            "take_paths": [str(take_low), str(take_best)],
            "out_dir": str(out_dir),
            "frame_length": 1024,
            "hop_length": 256,
            "segment_duration": 2.0,
        }
    )

    assert payload["summary"] is not None
    assert payload["session_summary"]["schema_version"] == 1
    assert payload["session_summary"]["compared_takes"] == 2
    assert payload["session_summary"]["best_take"]["take_path"].endswith("take_best.wav")
    assert payload["session_summary"]["weakest_take"]["take_path"].endswith("take_low.wav")
    assert payload["session_summary"]["next_recording_target"]
    assert payload["entries"]
    assert payload["entries"][0]["rank"] == 1
    assert payload["entries"][0]["take_path"].endswith("take_best.wav")
    assert payload["entries"][0]["input_suitability"]["schema_version"] == 1
    assert payload["entries"][0]["input_suitability"]["status"] in {"ok", "warning", "low_confidence"}
    assert isinstance(payload["entries"][0]["artifacts"], list)
    assert isinstance(payload["artifacts"], list)
    assert (out_dir / "batch_report.json").exists()
    assert (out_dir / "batch_report.md").exists()
    assert (out_dir / "batch_report.csv").exists()


def test_practice_session_payload_appends_history_entry(tmp_path: Path) -> None:
    reference = tmp_path / "reference.wav"
    take_best = tmp_path / "take_best.wav"
    take_low = tmp_path / "take_low.wav"
    out_dir = tmp_path / "practice-session-api-out"
    history_index = tmp_path / ".practicelens" / "sessions" / "index.jsonl"

    _write_wav(reference, 220.0)
    _write_wav(take_best, 220.0)
    _write_wav(take_low, 261.63)

    payload = practice_session_payload(
        {
            "reference_path": str(reference),
            "take_paths": [str(take_low), str(take_best)],
            "out_dir": str(out_dir),
            "history_index": str(history_index),
            "frame_length": 1024,
            "hop_length": 256,
            "segment_duration": 2.0,
        }
    )

    assert payload["summary"] is not None
    assert payload["session_summary"]["best_take"]["take_path"].endswith("take_best.wav")
    assert payload["history_index_path"] == str(history_index)
    assert payload["history_entry_appended"] is True
    assert (out_dir / "batch_report.json").exists()
    assert (out_dir / "practice_plan.md").exists()
    assert (out_dir / "session_manifest.json").exists()
    assert history_index.exists()

    history_entry = json.loads(history_index.read_text(encoding="utf-8").strip())
    assert history_entry["kind"] == "practice_session_index_entry"
    assert history_entry["session_dir"] == str(out_dir)
    assert history_entry["manifest_path"] == str(out_dir / "session_manifest.json")


def test_practice_session_payload_rejects_invalid_history_index_before_side_effects(tmp_path: Path) -> None:
    reference = tmp_path / "reference.wav"
    take_a = tmp_path / "take_a.wav"
    take_b = tmp_path / "take_b.wav"
    out_dir = tmp_path / "practice-session-api-out"

    _write_wav(reference, 220.0)
    _write_wav(take_a, 220.0)
    _write_wav(take_b, 261.63)

    with pytest.raises(ValueError, match="history_index must be a non-empty string"):
        practice_session_payload(
            {
                "reference_path": str(reference),
                "take_paths": [str(take_a), str(take_b)],
                "out_dir": str(out_dir),
                "history_index": "",
                "frame_length": 1024,
                "hop_length": 256,
                "segment_duration": 2.0,
            }
        )

    assert not out_dir.exists()


def test_practice_session_payload_requires_out_dir() -> None:
    with pytest.raises(ValueError, match="out_dir is required"):
        practice_session_payload(
            {
                "reference_path": "reference.wav",
                "take_paths": ["take_a.wav", "take_b.wav"],
            }
        )
