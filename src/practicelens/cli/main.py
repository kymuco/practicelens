from __future__ import annotations

import argparse
import sys
from pathlib import Path

from practicelens.application import (
    AnalyzeRequest,
    BatchCompareRequest,
    BatchCompareResult,
    OfflineBatchComparePipeline,
    OfflineReferenceAnalysisPipeline,
)
from practicelens.domain.enums import ArtifactKind
from practicelens.domain.models import AnalysisConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="practicelens")
    subparsers = parser.add_subparsers(dest="command")

    analyze = subparsers.add_parser("analyze", help="Analyze a take against a reference WAV.")
    analyze.add_argument("--reference", required=True, help="Path to the reference WAV file.")
    analyze.add_argument("--take", required=True, help="Path to the user take WAV file.")
    analyze.add_argument("--out", required=True, help="Output directory for report artifacts.")
    _add_common_analysis_args(analyze)

    compare_batch = subparsers.add_parser(
        "compare-batch",
        help="Compare multiple takes against one reference WAV.",
    )
    _add_batch_args(compare_batch, out_help="Output directory for batch artifacts.")
    _add_common_analysis_args(compare_batch)

    practice_session = subparsers.add_parser(
        "practice-session",
        help="Run a practice-session review across multiple takes.",
    )
    _add_batch_args(practice_session, out_help="Output directory for practice-session artifacts.")
    _add_common_analysis_args(practice_session)

    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "analyze":
        return _run_analyze(args)
    if args.command == "compare-batch":
        return _run_compare_batch(args)
    if args.command == "practice-session":
        return _run_practice_session(args)

    parser.print_help()
    return 1


def _run_analyze(args: argparse.Namespace) -> int:
    request = AnalyzeRequest(
        reference_path=Path(args.reference),
        take_path=Path(args.take),
        out_dir=Path(args.out),
        config=_build_config(args),
    )
    try:
        result = OfflineReferenceAnalysisPipeline().analyze(request)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result.report.summary or "Analysis completed.")
    for artifact in result.report.artifacts:
        print(f"{artifact.kind.value}: {artifact.path}")
    return 0


def _run_compare_batch(args: argparse.Namespace) -> int:
    try:
        result = _run_batch_compare_pipeline(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result.summary or "Batch comparison completed.")
    for kind, path in result.artifacts:
        print(f"{kind.value}: {path}")
    return 0


def _run_practice_session(args: argparse.Namespace) -> int:
    try:
        result = _run_batch_compare_pipeline(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result.summary or "Practice session completed.")
    if result.session_summary is not None:
        summary = result.session_summary
        print(f"best_take: {summary.best_take.take_path}")
        print(f"weakest_take: {summary.weakest_take.take_path}")
        print(f"recurring_weakness: {summary.recurring_weakness.value}")
        print(f"next_recording_target: {summary.next_recording_target}")
    practice_plan_path = _find_batch_artifact_path(result, ArtifactKind.PRACTICE_PLAN)
    if practice_plan_path is not None:
        print(f"practice_plan: {practice_plan_path}")
    return 0


def _run_batch_compare_pipeline(args: argparse.Namespace) -> BatchCompareResult:
    request = BatchCompareRequest(
        reference_path=Path(args.reference),
        take_paths=tuple(Path(value) for value in args.takes),
        out_dir=Path(args.out),
        config=_build_config(args),
    )
    return OfflineBatchComparePipeline().compare(request)


def _find_batch_artifact_path(result: BatchCompareResult, kind: ArtifactKind) -> Path | None:
    for artifact_kind, path in result.artifacts:
        if artifact_kind == kind:
            return path
    return None


def _build_config(args: argparse.Namespace) -> AnalysisConfig:
    return AnalysisConfig(
        target_sample_rate=args.sample_rate,
        frame_length=args.frame_length,
        hop_length=args.hop_length,
        segment_duration_s=args.segment_duration,
    )


def _add_batch_args(parser: argparse.ArgumentParser, *, out_help: str) -> None:
    parser.add_argument("--reference", required=True, help="Path to the reference WAV file.")
    parser.add_argument(
        "--take",
        dest="takes",
        action="append",
        required=True,
        help="Path to one take WAV file. Repeat for multiple takes.",
    )
    parser.add_argument("--out", required=True, help=out_help)


def _add_common_analysis_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--sample-rate", type=int, default=16_000)
    parser.add_argument("--frame-length", type=int, default=2_048)
    parser.add_argument("--hop-length", type=int, default=512)
    parser.add_argument("--segment-duration", type=float, default=8.0)


if __name__ == "__main__":
    raise SystemExit(run())