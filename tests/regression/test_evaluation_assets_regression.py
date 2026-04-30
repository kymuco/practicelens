from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from practicelens.application import AnalyzeRequest, OfflineReferenceAnalysisPipeline
from practicelens.domain.enums import MetricName
from practicelens.domain.models import AnalysisConfig, AnalysisReport
from practicelens.evaluation_assets import generate_evaluation_assets

EXPECTATIONS = json.loads((Path(__file__).with_name("evaluation_expectations.json")).read_text(encoding="utf-8"))


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


def _metric_value(report: AnalysisReport, metric: str) -> float:
    if metric == "overall_score":
        return _overall_score(report)
    return _score(report, MetricName(metric))


def test_generated_evaluation_cases_match_calibration_expectation_manifest(tmp_path: Path) -> None:
    assets = generate_evaluation_assets(tmp_path / "assets")
    reference = assets[EXPECTATIONS["reference_case"]]
    reports: dict[str, AnalysisReport] = {}

    for case in EXPECTATIONS["cases"]:
        case_name = case["name"]
        reports[case_name] = _run(reference, assets[case_name], tmp_path / f"{case_name}-out")

    for case in EXPECTATIONS["cases"]:
        report = reports[case["name"]]
        assert 0.0 <= _overall_score(report) <= 100.0
        assert report.summary is not None
        assert report.feedback
        assert report.artifacts
        if case.get("must_have_sections", False):
            assert report.sections
        _assert_minimum_overall_score(report, case)
        _assert_minimum_metric_scores(report, case)
        _assert_relative_expectations(report, reports, case)


def _assert_minimum_overall_score(report: AnalysisReport, case: dict[str, Any]) -> None:
    minimum = case.get("minimum_overall_score")
    if minimum is None:
        return
    assert _overall_score(report) >= minimum


def _assert_minimum_metric_scores(report: AnalysisReport, case: dict[str, Any]) -> None:
    minimum_metric_scores = case.get("minimum_metric_scores", {})
    for metric, minimum in minimum_metric_scores.items():
        assert _metric_value(report, metric) >= minimum


def _assert_relative_expectations(
    report: AnalysisReport,
    reports: dict[str, AnalysisReport],
    case: dict[str, Any],
) -> None:
    for expectation in case.get("relative_expectations", []):
        metric = expectation["metric"]
        baseline = reports[expectation["baseline"]]
        relation = expectation["relation"]
        if relation == "lower_than":
            assert _metric_value(report, metric) < _metric_value(baseline, metric)
        elif relation == "higher_than":
            assert _metric_value(report, metric) > _metric_value(baseline, metric)
        else:
            raise AssertionError(f"unsupported relative expectation relation: {relation}")
