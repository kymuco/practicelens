from __future__ import annotations

import os
from pathlib import Path

from practicelens.measurement.equivalence_floor import (
    render_synthetic_equivalence_floor_text,
    run_synthetic_equivalence_floor,
)


def main() -> None:
    result = run_synthetic_equivalence_floor(
        Path("out/synthetic_equivalence_floor_v1"),
        code_revision=(
            os.environ.get("PRACTICELENS_INSTRUMENT_REVISION")
            or os.environ.get("GITHUB_SHA")
        ),
    )
    print(render_synthetic_equivalence_floor_text(result.summary))
    print(f"summary: {result.summary_path}")


if __name__ == "__main__":
    main()
