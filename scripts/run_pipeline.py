#!/usr/bin/env python3
"""Run the full reproducible real-data-first research pipeline in canonical order."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PY = sys.executable

STEPS = [
    [PY, "scripts/01_prepare_real_panel.py"],
    [PY, "scripts/02_run_baseline_analysis.py"],
    [PY, "scripts/03_run_robustness_checks.py"],
    [PY, "scripts/04_generate_figures_tables.py"],
]


def main() -> None:
    for cmd in STEPS:
        print(f"\n>>> Running: {' '.join(cmd)}")
        proc = subprocess.run(cmd, cwd=ROOT, check=False)
        if proc.returncode != 0:
            print(f"Pipeline failed at: {' '.join(cmd)}", file=sys.stderr)
            sys.exit(proc.returncode)
    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    main()
