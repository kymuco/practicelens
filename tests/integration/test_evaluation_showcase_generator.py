from __future__ import annotations

import json
from pathlib import Path

from practicelens.evaluation_showcase import generate_evaluation_showcase


def _normalize_path_separators(value: str) -> str:
    """Normalize platform-native paths when tests assert path identity, not slash style."""

    return value.replace("\\", "/")


def test_generate_evaluation_showcase_writes_expected_outputs(tmp_path: Path) -> None:
    result = generate_evaluation_showcase(
        tmp_path / "showcase",
        case_names=("exact_take", "pitch_drift_take", "timing_drift_take"),
    )

    assert result.out_dir == tmp_path / "showcase"
    assert result.summary_path.exists()
    assert result.readme_path.exists()
    assert (result.assets_dir / "reference_phrase.wav").exists()
    assert (result.single_reports_dir / "exact_take" / "report.json").exists()
    assert (result.single_reports_dir / "pitch_drift_take" / "report.md").exists()
    assert (result.single_reports_dir / "pitch_drift_take" / "practice_plan.md").exists()
    assert (result.batch_dir / "batch_report.json").exists()
    assert (result.batch_dir / "batch_report.md").exists()
    assert (result.batch_dir / "practice_plan.md").exists()
    assert (result.batch_dir / "session_manifest.json").exists()
    assert (result.batch_dir / "batch_report.csv").exists()
    assert (result.batch_dir / "batch_report.svg").exists()

    summary = json.loads(result.summary_path.read_text(encoding="utf-8"))
    assert summary["schema_version"] == 1
    assert summary["reference_case"] == "reference_phrase"
    assert _normalize_path_separators(summary["batch_practice_plan_path"]).endswith("batch/practice_plan.md")
    assert summary["batch_session_summary"]["schema_version"] == 1
    assert summary["batch_session_summary"]["compared_takes"] == 3
    assert summary["batch_session_summary"]["best_take"]
    assert summary["batch_session_summary"]["next_recording_target"]
    assert [case["case_name"] for case in summary["cases"]] == [
        "exact_take",
        "pitch_drift_take",
        "timing_drift_take",
    ]
    assert len(summary["batch_ranking"]) == 3
    assert all("overall_score" in case for case in summary["cases"])
    assert all("practice_loops" in case for case in summary["cases"])

    batch_payload = json.loads((result.batch_dir / "batch_report.json").read_text(encoding="utf-8"))
    assert len(batch_payload["entries"]) == 3
    assert batch_payload["session_summary"]["schema_version"] == 1
    assert batch_payload["session_summary"]["compared_takes"] == 3
    assert batch_payload["session_summary"]["next_recording_target"]
    assert all("practice_loops" in entry for entry in batch_payload["entries"])
    assert {artifact["kind"] for artifact in batch_payload["artifacts"]} == {
        "json_report",
        "markdown_report",
        "csv_report",
        "svg_report",
        "practice_plan",
        "session_manifest",
    }

    manifest = json.loads((result.batch_dir / "session_manifest.json").read_text(encoding="utf-8"))
    assert manifest["kind"] == "practice_session_manifest"
    assert _normalize_path_separators(manifest["entrypoints"]["batch_json"]).endswith("batch/batch_report.json")
    assert _normalize_path_separators(manifest["entrypoints"]["practice_plan"]).endswith("batch/practice_plan.md")
    assert _normalize_path_separators(manifest["entrypoints"]["session_manifest"]).endswith("batch/session_manifest.json")

    generated_readme = _normalize_path_separators(result.readme_path.read_text(encoding="utf-8"))
    assert "# Generated Evaluation Showcase" in generated_readme
    assert "pitch_drift_take" in generated_readme
    assert "batch/practice_plan.md" in generated_readme
    assert "batch/batch_report.md" in generated_readme
