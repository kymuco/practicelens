from __future__ import annotations

import csv
import io
import json

from practicelens.application.contracts import BatchCompareResult


def batch_compare_result_to_json_payload(result: BatchCompareResult) -> dict[str, object]:
    entries = [
        {
            "rank": entry.rank,
            "take_path": str(entry.take_path),
            "overall_score": entry.overall_score,
            "summary": entry.summary,
            "output_dir": str(entry.output_dir) if entry.output_dir is not None else None,
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
        "reference_path": str(result.reference_path),
        "summary": result.summary,
        "entries": entries,
        "artifacts": [
            {"kind": kind.value, "path": str(path)}
            for kind, path in result.artifacts
        ],
    }


def batch_compare_result_to_json_text(result: BatchCompareResult) -> str:
    return json.dumps(batch_compare_result_to_json_payload(result), indent=2, sort_keys=True)


def batch_compare_result_to_markdown(result: BatchCompareResult) -> str:
    lines = ["# PracticeLens Batch Compare", ""]
    lines.append(f"**Reference:** `{result.reference_path}`")
    if result.summary:
        lines.extend(["", result.summary])
    lines.extend(["", "## Ranking", ""])
    for entry in result.entries:
        lines.append(
            f"- **#{entry.rank}** `{entry.take_path.name}` — {entry.overall_score:.1f}/100"
        )
        if entry.summary:
            lines.append(f"  - {entry.summary}")
    if result.artifacts:
        lines.extend(["", "## Batch Artifacts", ""])
        for kind, path in result.artifacts:
            lines.append(f"- **{kind.value}**: `{path}`")
    return "\n".join(lines).rstrip() + "\n"


def batch_compare_result_to_csv_text(result: BatchCompareResult) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["rank", "take_path", "overall_score", "summary", "output_dir"])
    for entry in result.entries:
        writer.writerow(
            [
                entry.rank,
                str(entry.take_path),
                f"{entry.overall_score:.3f}",
                entry.summary or "",
                str(entry.output_dir) if entry.output_dir is not None else "",
            ]
        )
    return buffer.getvalue()
