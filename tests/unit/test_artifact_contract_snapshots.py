from __future__ import annotations

from pathlib import Path

from .._helpers import read_json


def test_single_example_artifact_files_exist_and_have_expected_markdown_sections() -> None:
    result_dir = Path("examples/results/single")
    report = read_json(result_dir / "report.json")

    _assert_artifact_targets_exist(report["artifacts"])

    report_md = (result_dir / "report.md").read_text(encoding="utf-8")
    practice_plan_md = (result_dir / "practice_plan.md").read_text(encoding="utf-8")
    debug_payload = read_json(result_dir / "debug_payload.json")

    _assert_markdown_headings(
        report_md,
        (
            "# PracticeLens Report",
            "## At a glance",
            "## Analysis Confidence",
            "## Practice Loops",
            "## Component Scores",
            "## Artifacts",
        ),
    )
    _assert_markdown_headings(
        practice_plan_md,
        (
            "# PracticeLens Practice Plan",
            "## Goal for the next take",
            "## Current take snapshot",
            "## Practice loops",
            "## Next recording target",
            "## Confidence notes",
        ),
    )
    assert debug_payload["kind"] == "debug_payload"
    assert debug_payload["schema_version"] == 1
    assert debug_payload["score_summary"]["overall_score"] == report["overall_score"]


def test_batch_example_artifact_files_exist_and_have_expected_markdown_sections() -> None:
    result_dir = Path("examples/results/batch")
    report = read_json(result_dir / "batch_report.json")

    _assert_artifact_targets_exist(report["artifacts"])

    batch_report_md = (result_dir / "batch_report.md").read_text(encoding="utf-8")
    practice_plan_md = (result_dir / "practice_plan.md").read_text(encoding="utf-8")

    _assert_markdown_headings(
        batch_report_md,
        (
            "# PracticeLens Batch Compare",
            "## At a glance",
            "## Session decision",
            "## Recommended session loops",
            "## Ranking",
            "## Take summaries",
            "## Batch Artifacts",
        ),
    )
    _assert_markdown_headings(
        practice_plan_md,
        (
            "# PracticeLens Batch Practice Plan",
            "## Session goal",
            "## Keep take",
            "## Recurring weakness across takes",
            "## Strongest stable area",
            "## Top practice loops",
            "## Next recording target",
            "## Take ranking snapshot",
        ),
    )
    assert report["session_summary"]["schema_version"] == 1
    assert report["session_summary"]["practice_loops"]


def _assert_artifact_targets_exist(artifacts: list[dict[str, object]]) -> None:
    for artifact in artifacts:
        path = artifact["path"]
        assert isinstance(path, str)
        assert Path(path).exists(), f"missing artifact fixture: {path}"


def _assert_markdown_headings(markdown_text: str, headings: tuple[str, ...]) -> None:
    for heading in headings:
        assert heading in markdown_text
