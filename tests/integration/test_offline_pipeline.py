import json
import math
import wave
from pathlib import Path

from practicelens.application import AnalyzeRequest, OfflineReferenceAnalysisPipeline
from practicelens.domain.models import AnalysisConfig


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


def test_offline_pipeline_generates_report_artifacts(tmp_path: Path) -> None:
    reference = tmp_path / "reference.wav"
    take = tmp_path / "take.wav"
    out_dir = tmp_path / "out"

    reference_samples = [math.sin(2.0 * math.pi * 220.0 * index / 16_000.0) for index in range(8000)]
    take_samples = [math.sin(2.0 * math.pi * 220.0 * index / 16_000.0) for index in range(8000)]
    _write_wav(reference, reference_samples)
    _write_wav(take, take_samples)

    pipeline = OfflineReferenceAnalysisPipeline()
    result = pipeline.analyze(
        AnalyzeRequest(
            reference_path=reference,
            take_path=take,
            out_dir=out_dir,
            config=AnalysisConfig(frame_length=1024, hop_length=256, segment_duration_s=2.0),
        )
    )

    assert result.report.summary is not None
    assert result.report.analysis_confidence.level in {"high", "medium", "low"}
    assert result.report.analysis_confidence.reasons
    assert result.report.analysis_confidence.limitations
    assert result.report.top_strengths
    assert result.report.top_weaknesses
    assert result.report.next_practice_step is not None
    assert len(result.report.artifacts) == 4
    assert (out_dir / "report.json").exists()
    assert (out_dir / "report.md").exists()
    assert (out_dir / "report.csv").exists()
    assert (out_dir / "report.svg").exists()

    payload = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
    assert set(payload) == {
        "overview",
        "inputs",
        "feature_flags",
        "overall_score",
        "scores",
        "metrics",
        "sections",
        "analysis_confidence",
        "top_strengths",
        "top_weaknesses",
        "next_practice_step",
        "feedback",
        "artifacts",
        "summary",
    }
    assert payload["overview"] == {
        "kind": "analysis_report",
        "schema_version": 1,
        "status": "completed",
        "ok": True,
        "mode": "reference",
    }
    assert payload["analysis_confidence"]["level"] in {"high", "medium", "low"}
    assert payload["analysis_confidence"]["reasons"]
    assert payload["analysis_confidence"]["limitations"]
