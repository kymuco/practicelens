from __future__ import annotations

import argparse
import os
from pathlib import Path

from practicelens.measurement.local_session_repeatability import (
    LOCAL_SESSION_REPEATABILITY_RECOMMENDED_TAKES,
    render_local_session_repeatability_text,
    run_local_session_repeatability,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the local R0.5b within-session repeatability experiment.",
    )
    parser.add_argument("--reference", required=True, help="Reference WAV path.")
    parser.add_argument(
        "--take",
        dest="takes",
        action="append",
        required=True,
        help=(
            "Independent same-session take WAV. Repeat this argument; "
            f"{LOCAL_SESSION_REPEATABILITY_RECOMMENDED_TAKES} takes are recommended."
        ),
    )
    parser.add_argument(
        "--out",
        default="out/local_session_repeatability_v1.json",
        help="Output JSON evidence path. Raw audio is never copied into this artifact.",
    )
    parser.add_argument(
        "--session-label",
        default=None,
        help="Optional non-sensitive local label for the session.",
    )
    args = parser.parse_args()

    result = run_local_session_repeatability(
        Path(args.reference),
        tuple(Path(value) for value in args.takes),
        out_path=Path(args.out),
        session_label=args.session_label,
        code_revision=os.environ.get("PRACTICELENS_INSTRUMENT_REVISION"),
    )
    print(render_local_session_repeatability_text(result.summary))
    print(f"evidence: {result.summary_path}")


if __name__ == "__main__":
    main()
