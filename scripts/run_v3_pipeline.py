#!/usr/bin/env python3
"""Run reproducible v3 identification sweep pipeline.

Default behavior includes a long-horizon GH Archive refresh and then the full
multi-proxy/multi-method estimation sweep.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


def _run(cmd: list[str]) -> None:
    print(f">>> Running: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=ROOT, check=False)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run v3 long-horizon identification sweep pipeline")
    parser.add_argument("--skip-fetch", action="store_true", help="Skip GH Archive fetch and use existing long-horizon raw panel")
    parser.add_argument("--start-date", default="2023-11-01")
    parser.add_argument("--end-date", default="2025-04-30")
    parser.add_argument("--hour-step", type=int, default=24)
    parser.add_argument("--max-lines-per-hour", type=int, default=120000)
    parser.add_argument("--lead-max", type=int, default=6)
    parser.add_argument("--lag-max", type=int, default=8)
    parser.add_argument("--stack-pre", type=int, default=6)
    parser.add_argument("--stack-post", type=int, default=8)
    args = parser.parse_args()

    if not args.skip_fetch:
        _run(
            [
                PY,
                "scripts/00_fetch_long_horizon_panel.py",
                "--start-date",
                args.start_date,
                "--end-date",
                args.end_date,
                "--hour-step",
                str(args.hour_step),
                "--max-lines-per-hour",
                str(args.max_lines_per_hour),
            ]
        )

    _run(
        [
            PY,
            "scripts/06_run_v3_identification_sweep.py",
            "--lead-max",
            str(args.lead_max),
            "--lag-max",
            str(args.lag_max),
            "--stack-pre",
            str(args.stack_pre),
            "--stack-post",
            str(args.stack_post),
        ]
    )

    print("\nV3 identification sweep completed successfully.")


if __name__ == "__main__":
    main()
