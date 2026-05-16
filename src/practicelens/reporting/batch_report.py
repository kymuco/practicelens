from __future__ import annotations

import csv
import io
import json

from practicelens.application.contracts import BatchCompareResult, BatchSessionSummary, SessionPracticeLoopSummary, SessionTakeSummary
from practicelens.domain.enums import ArtifactKind
from practicelens.domain.models import PracticeLoop


def batch_compare_result_to_json_payload(result: BatchCompareResult) -> dict[str, object]:
    entries = [
        {
            "rank": entry.rank,
            "take_path": str(entry.take_path),
            "overall_score": entry.overall_score,
            "summary": entry.summary,
            "output_dir": str(entry.output_dir) if entry.output_dir is not None else None,
            "practice_loops": [_practice_loop_payload(loop) for loop in entry.result.report.practice_loops],
            "artifacts": [
                {
                    "kind": artifact.kind.value,
                    "path": artifact.path,
                    "description": artifact.description,
                }
                for artifact in entry.result.report.artifacts
            ],
        }
        for entry in result.entries
    ]
    return {
        "overview": {
            "kind": result.overview.kind,
            "schema_version": int(result.overview.schema_version),
            "status": result.overview.status,
            "ok": result.overview.ok,
        },
        "reference_path": str(result.reference_path),
        "summary": result.summary,
        "session_summary": _session_summary_payload(result.session_summary),
        "entries": entries,
        "artifacts": [
            {
                "kind": kind.value,
                "path": str(path),
                "description": _batch_artifact_description(kind),
            }
            for kind, path in result.artifacts
        ],
    }


def batch_compare_result_to_json_text(result: BatchCompareResult) -> str:
    return json.dumps(batch_compare_result_to_json_payload(result), indent=2, sort_keys=True)


def batch_compare_result_to_markdown(result: BatchCompareResult) -> str:
    best_score = result.entries[0].overall_score if result.entries else 0.0
    lines = ["# PracticeLens Batch Compare", ""]
    lines.append("## At a glance")
    lines.append("")
    lines.append(f"- **Reference:** `{result.reference_path}`")
    lines.append(f"- **Compared takes:** {len(result.entries)}")
    if result.entries:
        lines.append(f"- **Best take:** `{result.entries[0].take_path.name}`")
        lines.append(f"- **Best score:** {best_score:.1f}/100")
    if result.session_summary is not None:
        lines.append(f"- **Recurring weakness:** {_metric_label(result.session_summary.recurring_weakness.value)}")
        lines.append(f"- **Strongest stable area:** {_metric_label(result.session_summary.strongest_stable_area.value)}")
        lines.append(f"- **Next target:** {result.session_summary.next_recording_target}")
    if result.summary:
        lines.extend(["", result.summary])

    lines.extend(["", "## Ranking", ""])
    lines.append("| Rank | Take | Score | Delta vs best | Output dir |")
    lines.append("| --- | --- | ---: | ---: | --- |")
    for entry in result.entries:
        delta = best_score - entry.overall_score
        output_dir = f"`{entry.output_dir}`" if entry.output_dir is not None else "-"
        lines.append(
            f"| {entry.rank} | `{entry.take_path.name}` | {entry.overall_score:.1f} | {delta:.1f} | {output_dir} |"
        )

    lines.extend(["", "## Take summaries", ""])
    for entry in result.entries:
        lines.append(f"### #{entry.rank} `{entry.take_path.name}`")
        lines.append("")
        lines.append(f"- Score: {entry.overall_score:.1f}/100")
        if entry.summary:
            lines.append(f"- Summary: {entry.summary}")
        if entry.result.report.practice_loops:
            first_loop = entry.result.report.practice_loops[0]
            lines.append(f"- First practice loop: {first_loop.instruction}")
            lines.append(f"- Practice loops: {len(entry.result.report.practice_loops)}")
        else:
            lines.append("- Practice loops: none")
        lines.append(f"- Artifacts: {len(entry.result.report.artifacts)}")
        lines.append("")

    if result.artifacts:
        lines.extend(["## Batch Artifacts", ""])
        for kind, path in result.artifacts:
            lines.append(f"- **{kind.value}**: `{path}`")
    return "\n".join(lines).rstrip() + "\n"


def batch_compare_result_to_csv_text(result: BatchCompareResult) -> str:
    best_score = result.entries[0].overall_score if result.entries else 0.0
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "rank",
            "take_name",
            "take_path",
            "overall_score",
            "delta_from_best",
            "first_practice_loop",
            "summary",
            "output_dir",
        ]
    )
    for entry in result.entries:
        first_loop = entry.result.report.practice_loops[0].instruction if entry.result.report.practice_loops else ""
        writer.writerow(
            [
                entry.rank,
                entry.take_path.name,
                str(entry.take_path),
                f"{entry.overall_score:.3f}",
                f"{best_score - entry.overall_score:.3f}",
                first_loop,
                entry.summary or "",
                str(entry.output_dir) if entry.output_dir is not None else "",
            ]
        )
    return buffer.getvalue()


def _session_summary_payload(summary: BatchSessionSummary | None) -> dict[str, object] | None:
    if summary is None:
        return None
    return {
        "schema_version": summary.schema_version,
        "compared_takes": summary.compared_takes,
        "best_take": _take_summary_payload(summary.best_take),
        "weakest_take": _take_summary_payload(summary.weakest_take),
        "recurring_weakness": summary.recurring_weakness.value,
        "recurring_weakness_count": summary.recurring_weakness_count,
        "strongest_stable_area": summary.strongest_stable_area.value,
        "strongest_stable_area_average_score": summary.strongest_stable_area_average_score,
        "next_recording_target": summary.next_recording_target,
        "practice_loops": [_session_practice_loop_payload(loop) for loop in summary.practice_loops],
    }


def _take_summary_payload(take: SessionTakeSummary) -> dict[str, object]:
    return {
        "rank": take.rank,
        "take_path": str(take.take_path),
        "overall_score": take.overall_score,
    }


def _session_practice_loop_payload(loop: SessionPracticeLoopSummary) -> dict[str, object]:
    return {
        "take_rank": loop.take_rank,
        "take_path": str(loop.take_path),
        "section_index": loop.section_index,
        "start_s": loop.start_s,
        "end_s": loop.end_s,
        "focus": loop.focus.value,
        "instruction": loop.instruction,
    }


def _practice_loop_payload(loop: PracticeLoop) -> dict[str, object]:
    return {
        "section_index": loop.section_index,
        "start_s": loop.start_s,
        "end_s": loop.end_s,
        "focus": loop.focus.value,
        "instruction": loop.instruction,
    }


def _batch_artifact_description(kind: ArtifactKind) -> str | None:
    descriptions = {
        ArtifactKind.JSON_REPORT: "Structured batch comparison report.",
        ArtifactKind.MARKDOWN_REPORT: "Human-readable batch comparison report.",
        ArtifactKind.CSV_REPORT: "Take ranking table export.",
        ArtifactKind.SVG_REPORT: "Compact visual batch ranking summary.",
        ArtifactKind.PRACTICE_PLAN: "Session-level practice plan across compared takes.",
    }
    return descriptions.get(kind)


def _metric_label(raw_name: str) -> str:
    return raw_name.replace("_", " ").title()
