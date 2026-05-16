from __future__ import annotations

from pathlib import Path
from re import sub

from practicelens.application.batch_session_summary import build_batch_session_summary
from practicelens.application.contracts import (
    AnalyzeRequest,
    BatchCompareEntry,
    BatchCompareRequest,
    BatchCompareResult,
)
from practicelens.application.offline_pipeline import OfflineReferenceAnalysisPipeline
from practicelens.domain.enums import ArtifactKind
from practicelens.reporting.batch_practice_plan import batch_compare_result_to_practice_plan_markdown
from practicelens.reporting.batch_report import (
    batch_compare_result_to_csv_text,
    batch_compare_result_to_json_text,
    batch_compare_result_to_markdown,
)
from practicelens.reporting.batch_svg_report import batch_compare_result_to_svg
from practicelens.reporting.session_manifest import batch_compare_result_to_session_manifest_text


class OfflineBatchComparePipeline:
    """Run one reference against multiple takes and rank the results."""

    def __init__(self) -> None:
        self._single = OfflineReferenceAnalysisPipeline()

    def compare(self, request: BatchCompareRequest) -> BatchCompareResult:
        entries: list[BatchCompareEntry] = []
        for index, take_path in enumerate(request.take_paths, start=1):
            take_out_dir = None
            if request.out_dir is not None:
                take_out_dir = request.out_dir / "takes" / self._take_directory_name(index, take_path)

            analyze_result = self._single.analyze(
                AnalyzeRequest(
                    reference_path=request.reference_path,
                    take_path=take_path,
                    out_dir=take_out_dir,
                    config=request.config,
                )
            )
            overall_score = sum(score.score * score.weight for score in analyze_result.report.scores)
            entries.append(
                BatchCompareEntry(
                    rank=0,
                    take_path=take_path,
                    overall_score=overall_score,
                    result=analyze_result,
                    output_dir=take_out_dir,
                )
            )

        ranked_entries = tuple(
            BatchCompareEntry(
                rank=rank,
                take_path=entry.take_path,
                overall_score=entry.overall_score,
                result=entry.result,
                output_dir=entry.output_dir,
            )
            for rank, entry in enumerate(
                sorted(entries, key=lambda item: item.overall_score, reverse=True),
                start=1,
            )
        )

        result = BatchCompareResult(
            reference_path=request.reference_path,
            entries=ranked_entries,
            artifacts=(),
            summary=self._summary(ranked_entries),
            session_summary=build_batch_session_summary(ranked_entries),
        )

        if request.out_dir is not None:
            result = self._write_batch_artifacts(result, request.out_dir)

        return result

    def _write_batch_artifacts(self, result: BatchCompareResult, out_dir: Path) -> BatchCompareResult:
        out_dir.mkdir(parents=True, exist_ok=True)
        json_path = out_dir / "batch_report.json"
        markdown_path = out_dir / "batch_report.md"
        csv_path = out_dir / "batch_report.csv"
        svg_path = out_dir / "batch_report.svg"
        practice_plan_path = out_dir / "practice_plan.md"
        session_manifest_path = out_dir / "session_manifest.json"

        result_with_artifacts = BatchCompareResult(
            reference_path=result.reference_path,
            entries=result.entries,
            overview=result.overview,
            artifacts=(
                (ArtifactKind.JSON_REPORT, json_path),
                (ArtifactKind.MARKDOWN_REPORT, markdown_path),
                (ArtifactKind.CSV_REPORT, csv_path),
                (ArtifactKind.SVG_REPORT, svg_path),
                (ArtifactKind.PRACTICE_PLAN, practice_plan_path),
                (ArtifactKind.SESSION_MANIFEST, session_manifest_path),
            ),
            summary=result.summary,
            session_summary=result.session_summary,
        )

        json_path.write_text(batch_compare_result_to_json_text(result_with_artifacts), encoding="utf-8")
        markdown_path.write_text(batch_compare_result_to_markdown(result_with_artifacts), encoding="utf-8")
        csv_path.write_text(batch_compare_result_to_csv_text(result_with_artifacts), encoding="utf-8")
        svg_path.write_text(batch_compare_result_to_svg(result_with_artifacts), encoding="utf-8")
        practice_plan_path.write_text(batch_compare_result_to_practice_plan_markdown(result_with_artifacts), encoding="utf-8")
        session_manifest_path.write_text(batch_compare_result_to_session_manifest_text(result_with_artifacts), encoding="utf-8")

        return result_with_artifacts

    def _summary(self, entries: tuple[BatchCompareEntry, ...]) -> str:
        best = entries[0]
        return (
            f"Best take: {best.take_path.name} with {best.overall_score:.1f}/100 "
            f"across {len(entries)} compared takes."
        )

    def _take_directory_name(self, index: int, take_path: Path) -> str:
        stem = sub(r"[^a-zA-Z0-9._-]+", "-", take_path.stem).strip("-") or "take"
        return f"{index:02d}-{stem}"