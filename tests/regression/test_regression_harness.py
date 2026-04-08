import json
import math
import wave
from pathlib import Path

from practicelens.application import AnalyzeRequest, BatchCompareRequest, OfflineBatchComparePipeline, OfflineReferenceAnalysisPipeline
from practicelens.domain.enums import ArtifactKind, MetricName
from practicelens.domain.models import AnalysisConfig, AnalysisReport

EXPECTATIONS = json.loads((Path(__file__).with_name("expectations.json")).read_text(encoding="utf-8"))


def _write_sine_wav(path: Path, freq_hz: float, *, sample_rate: int = 16_000, duration_samples: int = 8000) -> None:
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


def _run_single(reference: Path, take: Path, out_dir: Path) -> AnalysisReport:
    return OfflineReferenceAnalysisPipeline().analyze(
        AnalyzeRequest(
            reference_path=reference,
            take_path=take,
            out_dir=out_dir,
            config=AnalysisConfig(frame_length=1024, hop_length=256, segment_duration_s=2.0),
        )
    ).report


def _overall_score(report: AnalysisReport) -> float:
    return sum(score.score * score.weight for score in report.scores)


def _score_by_name(report: AnalysisReport, metric_name: MetricName) -> float:
    for score in report.scores:
        if score.name == metric_name:
            return score.score
    raise AssertionError(f"missing component score for {metric_name.value}")


def test_exact_reference_match_stays_in_high_sanity_band(tmp_path: Path) -> None:
    reference = tmp_path / "reference.wav"
    take = tmp_path / "take.wav"
    out_dir = tmp_path / "single-out"

    _write_sine_wav(reference, 220.0)
    _write_sine_wav(take, 220.0)

    report = _run_single(reference, take, out_dir)

    expected = EXPECTATIONS["exact_reference_match"]
    assert _overall_score(report) >= expected["overall_score_min"]
    assert _score_by_name(report, MetricName.PITCH_FIDELITY) >= expected["pitch_fidelity_min"]


def test_shifted_pitch_take_scores_worse_than_exact_match(tmp_path: Path) -> None:
    reference = tmp_path / "reference.wav"
    take_exact = tmp_path / "take_exact.wav"
    take_shifted = tmp_path / "take_shifted.wav"

    _write_sine_wav(reference, 220.0)
    _write_sine_wav(take_exact, 220.0)
    _write_sine_wav(take_shifted, 261.63)

    exact_report = _run_single(reference, take_exact, tmp_path / "exact-out")
    shifted_report = _run_single(reference, take_shifted, tmp_path / "shifted-out")

    expected = EXPECTATIONS["exact_vs_shifted_single"]
    assert _overall_score(exact_report) - _overall_score(shifted_report) >= expected["min_overall_gap"]
    assert (
        _score_by_name(exact_report, MetricName.PITCH_FIDELITY)
        - _score_by_name(shifted_report, MetricName.PITCH_FIDELITY)
        >= expected["min_pitch_gap"]
    )


def test_three_take_ranking_stays_stable_for_synthetic_case(tmp_path: Path) -> None:
    reference = tmp_path / "reference.wav"
    take_best = tmp_path / "take_best.wav"
    take_mid = tmp_path / "take_mid.wav"
    take_low = tmp_path / "take_low.wav"
    out_dir = tmp_path / "batch-out"

    _write_sine_wav(reference, 220.0)
    _write_sine_wav(take_best, 220.0)
    _write_sine_wav(take_mid, 233.08)
    _write_sine_wav(take_low, 261.63)

    result = OfflineBatchComparePipeline().compare(
        BatchCompareRequest(
            reference_path=reference,
            take_paths=(take_mid, take_best, take_low),
            out_dir=out_dir,
            config=AnalysisConfig(frame_length=1024, hop_length=256, segment_duration_s=2.0),
        )
    )

    expected = EXPECTATIONS["three_take_ranking"]
    actual_order = [entry.take_path.name for entry in result.entries]
    assert actual_order == expected["expected_order"]
    assert result.entries[0].overall_score >= expected["best_score_min"]
    assert result.entries[0].overall_score - result.entries[-1].overall_score >= expected["min_gap_best_vs_worst"]
    assert result.summary is not None
    assert result.entries[0].take_path.name in result.summary

    artifact_kinds = [kind.value for kind, _ in result.artifacts]
    assert artifact_kinds == expected["expected_artifact_kinds"]
    assert any(kind == ArtifactKind.SVG_REPORT for kind, _ in result.artifacts)
