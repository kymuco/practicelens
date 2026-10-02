from __future__ import annotations

import os
from pathlib import Path

from practicelens.measurement.metric_specific_alignment_readout import (
    render_metric_specific_alignment_readout_text,
    run_metric_specific_alignment_readout_ablation,
)


def main() -> None:
    result = run_metric_specific_alignment_readout_ablation(
        Path("out/metric_specific_alignment_readout_v1"),
        code_revision=(
            os.environ.get("PRACTICELENS_INSTRUMENT_REVISION")
            or os.environ.get("GITHUB_SHA")
        ),
    )
    print(render_metric_specific_alignment_readout_text(result.summary))
    print(f"summary: {result.summary_path}")


if __name__ == "__main__":
    main()
