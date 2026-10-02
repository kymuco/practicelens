from __future__ import annotations

import os
from pathlib import Path

from practicelens.measurement.alignment_substrate_ablation import (
    render_alignment_substrate_ablation_text,
    run_alignment_substrate_ablation,
)


def main() -> None:
    result = run_alignment_substrate_ablation(
        Path("out/alignment_substrate_ablation_v1"),
        code_revision=(
            os.environ.get("PRACTICELENS_INSTRUMENT_REVISION")
            or os.environ.get("GITHUB_SHA")
        ),
    )
    print(render_alignment_substrate_ablation_text(result.summary))
    print(f"summary: {result.summary_path}")


if __name__ == "__main__":
    main()
