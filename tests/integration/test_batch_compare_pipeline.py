import json
import math
import wave
from pathlib import Path

from practicelens.application import BatchCompareRequest, OfflineBatchComparePipeline
from practicelens.domain.models import AnalysisConfig


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


def test_batch_compare_pipeline_ranks_multiple_takes(tmp_path: Path) -> None:
    reference = tmp_path / "reference.wav"
    take_best = tmp_path / "take_best.wav"
    take_mid = tmp_path / "take_mid.wav"
    take_low = tmp_path / "take_low.wav"
    out_dir = tmp_path / "batch-out"

    _write_wav(reference, 220.0)
    _write_wav(take_best, 220.0)
    _write_wav(take_mid, 233.08)
    _write_wav(take_low, 261.63)

    result = OfflineBatchComparePipeline().compare(
        BatchCompareRequest(
            reference_path=reference,
            take_paths=(take_mid, take_best, take_low),
            out_dir=out_dir,
            config=AnalysisConfig(frame_length=1024, hop_length=256, segment_duration_s=2.0),
        )
    )

    assert result.entries[0].take_path.name == "take_best.wav"
    assert result.entries[0].rank == 1
    assert len(result.entries) == 3
    assert (out_dir / "batch_report.json").exists()
    assert (out_dir / "batch_report.md").exists()
    assert (out_dir / "batch_report.csv").exists()
    assert (out_dir / "batch_report.svg").exists()
    assert (out_dir / "takes").exists()

    payload = json.loads((out_dir / "batch_report.json").read_text(encoding="utf-8"))
    assert set(payload) == {"overview", "reference_path", "summary", "entries", "artifacts"}
    assert payload["overview"] == {
        "kind": "batch_compare_report",
        "schema_version": 1,
        "status": "completed",
        "ok": True,
    }
    assert {artifact["kind"] for artifact in payload["artifacts"]} == {
        "json_report",
        "markdown_report",
        "csv_report",
        "svg_report",
    }
