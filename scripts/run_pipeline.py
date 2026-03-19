#!/usr/bin/env python3
"""Run the full reproducible research pipeline in canonical order."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    ["python3", "scripts/01_prepare_benchmark_moments.py"],
    ["python3", "scripts/02_generate_synthetic_data.py"],
    ["python3", "scripts/03_run_baseline_analysis.py"],
    ["python3", "scripts/04_run_robustness_checks.py"],
    ["python3", "scripts/05_generate_figures_tables.py"],
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
