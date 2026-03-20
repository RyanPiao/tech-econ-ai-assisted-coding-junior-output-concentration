#!/usr/bin/env python3
"""Fetch the long-horizon real-data panel from GH Archive for v3 identification sweep.

This is a thin reproducibility wrapper around the archived, validated extraction script.
It keeps provenance explicit by preserving the raw extraction metadata JSON.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch long-horizon real panel for v3 sweep")
    parser.add_argument("--start-date", default="2023-11-01")
    parser.add_argument("--end-date", default="2025-04-30")
    parser.add_argument("--repos-file", default="data/raw/real_proxy/repo_list_q2_2025_more_data.txt")
    parser.add_argument("--output-dir", default="data/raw/real_proxy")
    parser.add_argument("--hour-step", type=int, default=24)
    parser.add_argument("--hour-offset", type=int, default=0)
    parser.add_argument("--max-hours", type=int, default=None)
    parser.add_argument("--max-lines-per-hour", type=int, default=120000)
    parser.add_argument("--min-total-output", type=int, default=1)
    parser.add_argument("--request-timeout-sec", type=int, default=120)
    parser.add_argument("--tag", default="v3_long_h18")
    parser.add_argument("--out-panel", default="data/raw/real_proxy/repo_week_panel_v3_long_h18.csv")
    parser.add_argument("--out-metadata", default="data/raw/real_proxy/repo_week_panel_v3_long_h18_metadata.json")
    parser.add_argument("--out-dictionary", default="data/raw/real_proxy/repo_week_panel_v3_long_h18_dictionary.csv")
    args = parser.parse_args()

    legacy_script = ROOT / "archive/legacy_pre_rebuild_20260319/scripts/step2_real_pipeline.py"
    if not legacy_script.exists():
        raise FileNotFoundError(f"Missing legacy extraction script: {legacy_script}")

    cmd = [
        sys.executable,
        str(legacy_script),
        "--start-date",
        args.start_date,
        "--end-date",
        args.end_date,
        "--repos-file",
        str(ROOT / args.repos_file),
        "--output-dir",
        str(ROOT / args.output_dir),
        "--tag",
        args.tag,
        "--hour-step",
        str(args.hour_step),
        "--hour-offset",
        str(args.hour_offset),
        "--max-lines-per-hour",
        str(args.max_lines_per_hour),
        "--min-total-output",
        str(args.min_total_output),
        "--request-timeout-sec",
        str(args.request_timeout_sec),
    ]
    if args.max_hours is not None:
        cmd.extend(["--max-hours", str(args.max_hours)])

    print("Running:", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=ROOT, check=False)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)

    output_dir = ROOT / args.output_dir
    raw_panel = output_dir / f"step2_real_repo_week_panel_{args.tag}.csv"
    raw_dict = output_dir / f"step2_real_data_dictionary_{args.tag}.csv"
    raw_meta = output_dir / f"step2_real_metadata_{args.tag}.json"

    out_panel = ROOT / args.out_panel
    out_dict = ROOT / args.out_dictionary
    out_meta = ROOT / args.out_metadata

    out_panel.parent.mkdir(parents=True, exist_ok=True)
    out_dict.parent.mkdir(parents=True, exist_ok=True)
    out_meta.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(raw_panel, out_panel)
    shutil.copy2(raw_dict, out_dict)
    shutil.copy2(raw_meta, out_meta)

    print(f"Wrote {out_panel}")
    print(f"Wrote {out_dict}")
    print(f"Wrote {out_meta}")


if __name__ == "__main__":
    main()
