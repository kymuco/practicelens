from __future__ import annotations

import os
from pathlib import Path

from practicelens.measurement.additive_noise_attribution import (
    render_additive_noise_attribution_text,
    run_additive_noise_attribution_audit,
)


def main() -> None:
    result = run_additive_noise_attribution_audit(
        Path("out/additive_noise_attribution_v1"),
        code_revision=(
            os.environ.get("PRACTICELENS_INSTRUMENT_REVISION")
            or os.environ.get("GITHUB_SHA")
        ),
    )
    print(render_additive_noise_attribution_text(result.summary))
    print(f"summary: {result.summary_path}")


if __name__ == "__main__":
    main()
