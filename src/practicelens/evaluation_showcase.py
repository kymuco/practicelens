from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from practicelens.application import AnalyzeRequest, BatchCompareRequest, OfflineBatchComparePipeline, OfflineReferenceAnalysisPipeline
from practicelens.domain.models import AnalysisConfig
from practicelens.evaluation_assets import CASE_SPECS, REFERENCE_CASE, generate_evaluation_assets
from practicelens.reporting.batch_report import batch_compare_result_to_json_payload
from practicelens.reporting.json_report import report_to_json_payload

DEFAULT_SHOWCASE_OUT_DIR = Path("examples/evaluation_showcase/generated")
DEFAULT_SHOWCASE_CASES = (
    "exact_take",
    "pitch_drift_take",
    "timing_drift_take",
    "rhythm_mistake_take",
    "tempo_mismatch_take",
)
DEFAULT_SHOWCASE_CONFIG = AnalysisConfig(frame_length=1024, hop_length=256, segment_duration_s=1.0)


@dataclass(slots=True, frozen=True)
class EvaluationShowcaseResult:
    """Generated evaluation showcase output locations."""

    out_dir: Path
    assets_dir: Path
    single_reports_dir: Path
    batch_dir: Path
    summary_path: Path
    readme_path: Path


def generate_evaluation_showcase(
    out_dir: Path = DEFAULT_SHOWCASE_OUT_DIR,
    *,
    case_names: tuple[str, ...] = DEFAULT_SHOWCASE_CASES,
    config: AnalysisConfig = DEFAULT_SHOWCASE_CONFIG,
) -> EvaluationShowcaseResult:
    """Generate synthetic assets plus single and batch reports for showcase inspection."""

    out_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = out_dir / "assets"
    single_reports_dir = out_dir / "single"
    batch_dir = out_dir / "batch"

    assets = generate_evaluation_assets(assets_dir)
    reference = assets[REFERENCE_CASE]
    selected_case_names = _validate_case_names(case_names, assets)

    single_pipeline = OfflineReferenceAnalysisPipeline()
    single_outputs: list[dict[str, object]] = []
    for case_name in selected_case_names:
        case_out_dir = single_reports_dir / case_name
        result = single_pipeline.analyze(
            AnalyzeRequest(
                reference_path=reference,
                take_path=assets[case_name],
                out_dir=case_out_dir,
                config=config,
            )
        )
        payload = report_to_json_payload(result.report)
        single_outputs.append(
            {
                "case_name": case_name,
                "take_path": str(assets[case_name]),
                "out_dir": str(case_out_dir),
                "overall_score": payload["overall_score"],
                "summary": payload["summary"],
                "expected_weakness": _case_spec(case_name).expected_weakness,
                "practice_loops": payload["practice_loops"],
            }
        )

    batch_result = OfflineBatchComparePipeline().compare(
        BatchCompareRequest(
            reference_path=reference,
            take_paths=tuple(assets[case_name] for case_name in selected_case_names),
            out_dir=batch_dir,
            config=config,
        )
    )
    batch_payload = batch_compare_result_to_json_payload(batch_result)

    summary_path = out_dir / "summary.json"
    summary = {
        "schema_version": 1,
        "reference_case": REFERENCE_CASE,
        "reference_path": str(reference),
        "cases": single_outputs,
        "batch_report_path": str(batch_dir / "batch_report.json"),
        "batch_practice_plan_path": str(batch_dir / "practice_plan.md"),
        "batch_session_summary": batch_payload["session_summary"],
        "batch_ranking": [
            {
                "rank": entry["rank"],
                "take_path": entry["take_path"],
                "overall_score": entry["overall_score"],
                "practice_loops": entry["practice_loops"],
            }
            for entry in batch_payload["entries"]
        ],
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    readme_path = out_dir / "README.md"
    readme_path.write_text(_generated_readme(summary), encoding="utf-8")

    return EvaluationShowcaseResult(
        out_dir=out_dir,
        assets_dir=assets_dir,
        single_reports_dir=single_reports_dir,
        batch_dir=batch_dir,
        summary_path=summary_path,
        readme_path=readme_path,
    )


def _validate_case_names(case_names: tuple[str, ...], assets: dict[str, Path]) -> tuple[str, ...]:
    valid = tuple(case_name for case_name in case_names if case_name != REFERENCE_CASE)
    if not valid:
        raise ValueError("case_names must contain at least one non-reference case")
    unknown = sorted(case_name for case_name in valid if case_name not in assets)
    if unknown:
        raise ValueError(f"unknown evaluation showcase cases: {', '.join(unknown)}")
    return valid


def _case_spec(case_name: str):
    for spec in CASE_SPECS:
        if spec.name == case_name:
            return spec
    raise ValueError(f"unknown evaluation case: {case_name}")


def _generated_readme(summary: dict[str, object]) -> str:
    lines = [
        "# Generated Evaluation Showcase",
        "",
        "This directory was generated by `make generate-evaluation-showcase`.",
        "",
        "The files are synthetic and deterministic. They are useful for demos, smoke checks, and quick inspection.",
        "They are not a scientific benchmark and they do not replace real musician-recorded validation data.",
        "",
        "## What was generated",
        "",
        f"- Reference: `{summary['reference_path']}`",
        "- Synthetic WAV assets under `assets/`",
        "- Single-take reports and practice plans under `single/<case_name>/`",
        "- Batch comparison report and session practice plan under `batch/`",
        "- Machine-readable session summary in `summary.json`",
        "",
        "## Cases",
        "",
        "| Case | Overall score | Expected weakness | First practice loop |",
        "| --- | ---: | --- | --- |",
    ]
    for case in summary["cases"]:
        loops = case["practice_loops"]
        first_loop = loops[0]["instruction"] if loops else "-"
        lines.append(
            f"| `{case['case_name']}` | {case['overall_score']:.1f} | `{case['expected_weakness']}` | {first_loop} |"
        )
    lines.extend(
        [
            "",
            "## Suggested inspection path",
            "",
            "1. Open `summary.json` for the compact machine-readable session overview.",
            "2. Open `batch/practice_plan.md` for the session-level next action across takes.",
            "3. Open `batch/batch_report.md` for ranking details.",
            "4. Open the per-take `practice_plan.md` files for focused guidance.",
            "5. Open the matching `report.md` files when you want supporting analysis details.",
            "",
        ]
    )
    return "\n".join(lines)