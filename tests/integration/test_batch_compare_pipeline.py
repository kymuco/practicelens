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
    assert result.session_summary is not None
    assert result.session_summary.compared_takes == 3
    assert result.session_summary.best_take.take_path.name == "take_best.wav"
    assert result.session_summary.weakest_take.take_path.name == "take_low.wav"
    assert result.session_summary.next_recording_target
    assert result.session_summary.practice_loops
    assert (out_dir / "batch_report.json").exists()
    assert (out_dir / "batch_report.md").exists()
    assert (out_dir / "batch_report.csv").exists()
    assert (out_dir / "batch_report.svg").exists()
    assert (out_dir / "practice_plan.md").exists()
    assert (out_dir / "session_manifest.json").exists()
    assert (out_dir / "takes").exists()
    assert (out_dir / "takes" / "01-take_mid" / "practice_plan.md").exists()
    assert (out_dir / "takes" / "02-take_best" / "practice_plan.md").exists()
    assert (out_dir / "takes" / "03-take_low" / "practice_plan.md").exists()

    practice_plan = (out_dir / "practice_plan.md").read_text(encoding="utf-8")
    assert "# PracticeLens Batch Practice Plan" in practice_plan
    assert "## Recurring weakness across takes" in practice_plan
    assert "## Strongest stable area" in practice_plan
    assert "## Top practice loops" in practice_plan
    assert "## Next recording target" in practice_plan
    assert "take_best.wav" in practice_plan

    payload = json.loads((out_dir / "batch_report.json").read_text(encoding="utf-8"))
    assert set(payload) == {"overview", "reference_path", "summary", "session_summary", "entries", "artifacts"}
    assert payload["overview"] == {
        "kind": "batch_compare_report",
        "schema_version": 1,
        "status": "completed",
        "ok": True,
    }
    assert payload["session_summary"]["schema_version"] == 1
    assert payload["session_summary"]["compared_takes"] == 3
    assert payload["session_summary"]["best_take"]["take_path"].endswith("take_best.wav")
    assert payload["session_summary"]["weakest_take"]["take_path"].endswith("take_low.wav")
    assert payload["session_summary"]["recurring_weakness"]
    assert payload["session_summary"]["strongest_stable_area"]
    assert payload["session_summary"]["next_recording_target"]
    assert payload["session_summary"]["practice_loops"]
    assert {artifact["kind"] for artifact in payload["artifacts"]} == {
        "json_report",
        "markdown_report",
        "csv_report",
        "svg_report",
        "practice_plan",
        "session_manifest",
    }

    manifest = json.loads((out_dir / "session_manifest.json").read_text(encoding="utf-8"))
    assert manifest["kind"] == "practice_session_manifest"
    assert manifest["schema_version"] == 1
    assert manifest["compared_takes"] == 3
    assert manifest["best_take"]["take_path"].endswith("take_best.wav")
    assert manifest["weakest_take"]["take_path"].endswith("take_low.wav")
    assert manifest["next_recording_target"] == payload["session_summary"]["next_recording_target"]
    assert manifest["entrypoints"]["batch_json"].endswith("batch_report.json")
    assert manifest["entrypoints"]["batch_markdown"].endswith("batch_report.md")
    assert manifest["entrypoints"]["practice_plan"].endswith("practice_plan.md")
    assert manifest["entrypoints"]["session_manifest"].endswith("session_manifest.json")