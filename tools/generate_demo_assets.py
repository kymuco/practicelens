from __future__ import annotations

import argparse
from pathlib import Path

from practicelens.demo_assets import DEFAULT_OUT_DIR, generate_demo_assets


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic synthetic demo WAVs for PracticeLens.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_DIR, help="Output directory for generated demo assets.")
    args = parser.parse_args()

    paths = generate_demo_assets(args.out)
    for name, path in paths.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
