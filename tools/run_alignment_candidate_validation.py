from __future__ import annotations

import os
from pathlib import Path

from practicelens.measurement.alignment_candidate_validation import (
    render_alignment_candidate_validation_text,
    run_alignment_candidate_validation,
)


def main() -> None:
    result = run_alignment_candidate_validation(
        Path("out/alignment_candidate_validation_v1"),
        code_revision=(
            os.environ.get("PRACTICELENS_INSTRUMENT_REVISION")
            or os.environ.get("GITHUB_SHA")
        ),
    )
    print(render_alignment_candidate_validation_text(result.summary))
    print(f"summary: {result.summary_path}")


if __name__ == "__main__":
    main()
