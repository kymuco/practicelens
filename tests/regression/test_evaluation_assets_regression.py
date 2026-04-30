from __future__ import annotations

from pathlib import Path

from practicelens.application import AnalyzeRequest, OfflineReferenceAnalysisPipeline
from practicelens.domain.enums import MetricName
from practicelens.domain.models import AnalysisConfig, AnalysisReport
from practicelens.evaluation_assets import generate_evaluation_assets


def _run(reference: Path, take: Path, out_dir: Path) -> AnalysisReport:
    return OfflineReferenceAnalysisPipeline().analyze(
        AnalyzeRequest(
            reference_path=reference,
            take_path=take,
            out_dir=out_dir,
            config=AnalysisConfig(frame_length=1024, hop_length=256, segment_duration_s=1.0),
        )
    ).report


def _overall_score(report: AnalysisReport) -> float:
    return sum(score.score * score.weight for score in report.scores)


def _score(report: AnalysisReport, metric_name: MetricName) -> float:
    for score in report.scores:
        if score.name == metric_name:
            return score.score
    raise AssertionError(f"missing component score for {metric_name.value}")


def test_realistic_exact_take_remains_stronger_than_obvious_pitch_drift(tmp_path: Path) -> None:
    assets = generate_evaluation_assets(tmp_path / "assets")
    reference = assets["reference_phrase"]

    exact = _run(reference, assets["exact_take"], tmp_path / "exact-out")
    pitch_drift = _run(reference, assets["pitch_drift_take"], tmp_path / "pitch-drift-out")

    assert _overall_score(exact) > _overall_score(pitch_drift)
    assert _score(exact, MetricName.PITCH_FIDELITY) > _score(pitch_drift, MetricName.PITCH_FIDELITY)
    assert exact.sections
    assert pitch_drift.sections


def test_realistic_cases_are_pipeline_analyzable_without_locking_fragile_scores(tmp_path: Path) -> None:
    assets = generate_evaluation_assets(tmp_path / "assets")
    reference = assets["reference_phrase"]
    case_names = (
        "exact_take",
        "pitch_drift_take",
        "timing_drift_take",
        "rhythm_mistake_take",
        "noisy_take",
        "silence_mismatch_take",
        "vibrato_take",
        "pluck_take",
        "tempo_mismatch_take",
    )

    for case_name in case_names:
        report = _run(reference, assets[case_name], tmp_path / f"{case_name}-out")
        assert 0.0 <= _overall_score(report) <= 100.0
        assert report.summary is not None
        assert report.feedback
        assert report.sections
        assert report.artifacts
