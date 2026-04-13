from __future__ import annotations

import csv
import io
import json

from practicelens.application.contracts import BatchCompareResult
from practicelens.domain.enums import ArtifactKind


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
        "overview": {
            "kind": result.overview.kind,
            "schema_version": int(result.overview.schema_version),
            "status": result.overview.status,
            "ok": result.overview.ok,
        },
        "reference_path": str(result.reference_path),
        "summary": result.summary,
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
            "summary",
            "output_dir",
        ]
    )
    for entry in result.entries:
        writer.writerow(
            [
                entry.rank,
                entry.take_path.name,
                str(entry.take_path),
                f"{entry.overall_score:.3f}",
                f"{best_score - entry.overall_score:.3f}",
                entry.summary or "",
                str(entry.output_dir) if entry.output_dir is not None else "",
            ]
        )
    return buffer.getvalue()


def _batch_artifact_description(kind: ArtifactKind) -> str | None:
    descriptions = {
        ArtifactKind.JSON_REPORT: "Structured batch comparison report.",
        ArtifactKind.MARKDOWN_REPORT: "Human-readable batch comparison report.",
        ArtifactKind.CSV_REPORT: "Take ranking table export.",
        ArtifactKind.SVG_REPORT: "Compact visual batch ranking summary.",
    }
    return descriptions.get(kind)
