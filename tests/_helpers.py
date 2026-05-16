from __future__ import annotations

import json
import math
import wave
from pathlib import Path


def write_sine_wav(path: Path, freq_hz: float, *, sample_rate: int = 16_000, duration_samples: int = 8000) -> None:
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


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_artifacts(artifacts: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "kind": artifact["kind"],
            "description": artifact.get("description"),
        }
        for artifact in artifacts
    ]


def normalize_single_payload(payload: dict[str, object]) -> dict[str, object]:
    return {
        "top_level_keys": tuple(sorted(payload)),
        "overview": payload["overview"],
        "inputs": payload["inputs"],
        "feature_flags": payload["feature_flags"],
        "overall_score": payload["overall_score"],
        "scores": payload["scores"],
        "metrics": payload["metrics"],
        "sections": payload["sections"],
        "analysis_confidence": payload["analysis_confidence"],
        "practice_loops": payload["practice_loops"],
        "feedback": payload["feedback"],
        "artifacts": normalize_artifacts(payload["artifacts"]),
        "summary": payload["summary"],
    }


def normalize_batch_payload(payload: dict[str, object]) -> dict[str, object]:
    entries: list[dict[str, object]] = payload["entries"]
    return {
        "top_level_keys": tuple(sorted(payload)),
        "overview": payload["overview"],
        "reference_path": payload["reference_path"],
        "session_summary": payload["session_summary"],
        "entries": [
            {
                "rank": entry["rank"],
                "take_path": entry["take_path"],
                "overall_score": entry["overall_score"],
                "summary": entry["summary"],
                "practice_loops": entry["practice_loops"],
                "artifacts": normalize_artifacts(entry["artifacts"]),
            }
            for entry in entries
        ],
        "artifacts": normalize_artifacts(payload["artifacts"]),
        "summary": payload["summary"],
    }