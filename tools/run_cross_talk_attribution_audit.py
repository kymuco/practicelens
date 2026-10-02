from __future__ import annotations

import os
from pathlib import Path

from practicelens.measurement.cross_talk_attribution import (
    render_cross_talk_attribution_text,
    run_cross_talk_attribution_audit,
)


def main() -> None:
    result = run_cross_talk_attribution_audit(
        Path("out/cross_talk_attribution_v1"),
        code_revision=(
            os.environ.get("PRACTICELENS_INSTRUMENT_REVISION")
            or os.environ.get("GITHUB_SHA")
        ),
    )
    print(render_cross_talk_attribution_text(result.summary))
    print(f"summary: {result.summary_path}")


if __name__ == "__main__":
    main()
