from __future__ import annotations

import argparse
import sys
from pathlib import Path

from practicelens.application import (
    AnalyzeRequest,
    BatchCompareRequest,
    OfflineBatchComparePipeline,
    OfflineReferenceAnalysisPipeline,
)
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
    compare_batch.add_argument("--reference", required=True, help="Path to the reference WAV file.")
    compare_batch.add_argument(
        "--take",
        dest="takes",
        action="append",
        required=True,
        help="Path to one take WAV file. Repeat for multiple takes.",
    )
    compare_batch.add_argument("--out", required=True, help="Output directory for batch artifacts.")
    _add_common_analysis_args(compare_batch)

    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "analyze":
        return _run_analyze(args)
    if args.command == "compare-batch":
        return _run_compare_batch(args)

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
    request = BatchCompareRequest(
        reference_path=Path(args.reference),
        take_paths=tuple(Path(value) for value in args.takes),
        out_dir=Path(args.out),
        config=_build_config(args),
    )
    try:
        result = OfflineBatchComparePipeline().compare(request)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result.summary or "Batch comparison completed.")
    for kind, path in result.artifacts:
        print(f"{kind.value}: {path}")
    return 0


def _build_config(args: argparse.Namespace) -> AnalysisConfig:
    return AnalysisConfig(
        target_sample_rate=args.sample_rate,
        frame_length=args.frame_length,
        hop_length=args.hop_length,
        segment_duration_s=args.segment_duration,
    )


def _add_common_analysis_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--sample-rate", type=int, default=16_000)
    parser.add_argument("--frame-length", type=int, default=2_048)
    parser.add_argument("--hop-length", type=int, default=512)
    parser.add_argument("--segment-duration", type=float, default=8.0)


if __name__ == "__main__":
    raise SystemExit(run())
