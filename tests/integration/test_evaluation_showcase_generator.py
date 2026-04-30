from __future__ import annotations

import json
from pathlib import Path

from practicelens.evaluation_showcase import generate_evaluation_showcase


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
    assert (result.batch_dir / "batch_report.json").exists()
    assert (result.batch_dir / "batch_report.md").exists()
    assert (result.batch_dir / "batch_report.csv").exists()
    assert (result.batch_dir / "batch_report.svg").exists()

    summary = json.loads(result.summary_path.read_text(encoding="utf-8"))
    assert summary["schema_version"] == 1
    assert summary["reference_case"] == "reference_phrase"
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
    assert all("practice_loops" in entry for entry in batch_payload["entries"])

    generated_readme = result.readme_path.read_text(encoding="utf-8")
    assert "# Generated Evaluation Showcase" in generated_readme
    assert "pitch_drift_take" in generated_readme
    assert "batch/batch_report.md" in generated_readme
