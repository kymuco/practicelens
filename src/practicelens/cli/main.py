from __future__ import annotations

import argparse
import sys
from pathlib import Path

from practicelens.application import AnalyzeRequest, OfflineReferenceAnalysisPipeline
from practicelens.domain.models import AnalysisConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="practicelens")
    subparsers = parser.add_subparsers(dest="command")

    analyze = subparsers.add_parser("analyze", help="Analyze a take against a reference WAV.")
    analyze.add_argument("--reference", required=True, help="Path to the reference WAV file.")
    analyze.add_argument("--take", required=True, help="Path to the user take WAV file.")
    analyze.add_argument("--out", required=True, help="Output directory for report artifacts.")
    analyze.add_argument("--sample-rate", type=int, default=16_000)
    analyze.add_argument("--frame-length", type=int, default=2_048)
    analyze.add_argument("--hop-length", type=int, default=512)
    analyze.add_argument("--segment-duration", type=float, default=8.0)
    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command != "analyze":
        parser.print_help()
        return 1

    config = AnalysisConfig(
        target_sample_rate=args.sample_rate,
        frame_length=args.frame_length,
        hop_length=args.hop_length,
        segment_duration_s=args.segment_duration,
    )
    request = AnalyzeRequest(
        reference_path=Path(args.reference),
        take_path=Path(args.take),
        out_dir=Path(args.out),
        config=config,
    )

    try:
        pipeline = OfflineReferenceAnalysisPipeline()
        result = pipeline.analyze(request)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result.report.summary or "Analysis completed.")
    for artifact in result.report.artifacts:
        print(f"{artifact.kind.value}: {artifact.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
