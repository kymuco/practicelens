from __future__ import annotations

import os
from pathlib import Path

from practicelens.measurement.baseline_audit import (
    render_baseline_validity_audit_text,
    run_baseline_measurement_validity_audit,
)


def main() -> None:
    result = run_baseline_measurement_validity_audit(
        Path("out/measurement_validity_audit_v1"),
        code_revision=os.environ.get("GITHUB_SHA"),
    )
    print(render_baseline_validity_audit_text(result.summary))
    print(f"summary: {result.summary_path}")


if __name__ == "__main__":
    main()
