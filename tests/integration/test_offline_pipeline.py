import json
import math
import wave
from pathlib import Path

from practicelens.application import AnalyzeRequest, OfflineReferenceAnalysisPipeline
from practicelens.domain.models import AnalysisConfig
from practicelens.features import FeatureBundle


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
    assert result.report.input_suitability.status in {"ok", "warning", "low_confidence"}
    assert isinstance(result.report.practice_loops, tuple)
    assert result.report.top_strengths
    assert result.report.top_weaknesses
    assert result.report.next_practice_step is not None
    assert len(result.report.artifacts) == 6
    assert (out_dir / "report.json").exists()
    assert (out_dir / "report.md").exists()
    assert (out_dir / "report.csv").exists()
    assert (out_dir / "report.svg").exists()
    assert (out_dir / "practice_plan.md").exists()
    assert (out_dir / "debug_payload.json").exists()

    practice_plan = (out_dir / "practice_plan.md").read_text(encoding="utf-8")
    assert "# PracticeLens Practice Plan" in practice_plan
    assert "## Goal for the next take" in practice_plan
    assert "## Practice loops" in practice_plan
    assert "## Next recording target" in practice_plan

    debug_payload = json.loads((out_dir / "debug_payload.json").read_text(encoding="utf-8"))
    assert debug_payload["kind"] == "debug_payload"
    assert debug_payload["schema_version"] == 1
    assert debug_payload["score_summary"]["overall_score"] >= 0.0
    assert debug_payload["evidence_summary"]["section_count"] == len(result.report.sections)
    assert debug_payload["evidence_summary"]["input_suitability"]["status"] in {"ok", "warning", "low_confidence"}
    assert debug_payload["confidence"]["level"] in {"high", "medium", "low"}
    assert debug_payload["practice_guidance"]["next_practice_step"] == result.report.next_practice_step

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
        "input_suitability",
        "practice_loops",
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
    assert payload["input_suitability"]["schema_version"] == 1
    assert payload["input_suitability"]["status"] in {"ok", "warning", "low_confidence"}
    assert payload["input_suitability"]["reference_duration_s"] > 0.0
    assert payload["input_suitability"]["take_duration_s"] > 0.0
    assert isinstance(payload["practice_loops"], list)
    assert {artifact["kind"] for artifact in payload["artifacts"]} == {
        "json_report",
        "markdown_report",
        "csv_report",
        "svg_report",
        "practice_plan",
        "debug_payload",
    }


def test_offline_pipeline_reuses_reference_feature_extraction(
    tmp_path: Path,
    monkeypatch,
) -> None:
    import practicelens.application.offline_pipeline as offline_pipeline

    reference = tmp_path / "reference.wav"
    take_one = tmp_path / "take-one.wav"
    take_two = tmp_path / "take-two.wav"

    reference_samples = [math.sin(2.0 * math.pi * 220.0 * index / 16_000.0) for index in range(8000)]
    take_one_samples = [math.sin(2.0 * math.pi * 220.0 * index / 16_000.0) for index in range(8000)]
    take_two_samples = [math.sin(2.0 * math.pi * 233.08 * index / 16_000.0) for index in range(8000)]
    _write_wav(reference, reference_samples)
    _write_wav(take_one, take_one_samples)
    _write_wav(take_two, take_two_samples)

    original_extract = offline_pipeline.extract_feature_bundle
    extracted_bundles: list[FeatureBundle] = []

    def tracking_extract(*args, **kwargs):
        bundle = original_extract(*args, **kwargs)
        extracted_bundles.append(bundle)
        return bundle

    monkeypatch.setattr(offline_pipeline, "extract_feature_bundle", tracking_extract)

    pipeline = OfflineReferenceAnalysisPipeline()
    config = AnalysisConfig(frame_length=1024, hop_length=256, segment_duration_s=2.0)
    pipeline.analyze(AnalyzeRequest(reference_path=reference, take_path=take_one, config=config))
    pipeline.analyze(AnalyzeRequest(reference_path=reference, take_path=take_two, config=config))

    assert len(extracted_bundles) == 3
