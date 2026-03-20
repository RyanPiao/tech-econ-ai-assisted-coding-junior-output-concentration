#!/usr/bin/env python3
"""Generate calibrated synthetic panel data using benchmark moments."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.constants import DEFAULT_SEED
from src.io_helpers import load_moment_targets, write_json
from src.simulation import SimulationConfig, build_synthetic_panel


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic panel calibrated to benchmark moments")
    parser.add_argument("--moments", default="data/processed/benchmark_moments.csv")
    parser.add_argument("--out-panel", default="data/synthetic/synthetic_team_week_panel.csv")
    parser.add_argument("--out-meta", default="data/synthetic/synthetic_calibration_metadata.json")
    parser.add_argument("--out-diag", default="data/synthetic/synthetic_calibration_diagnostics.csv")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--n-teams", type=int, default=72)
    parser.add_argument("--n-weeks", type=int, default=30)
    parser.add_argument(
        "--treatment-effect",
        type=float,
        default=0.20,
        help="Treatment effect in latent share units; conservatively moderate by default",
    )
    args = parser.parse_args()

    moments_path = ROOT / args.moments
    out_panel = ROOT / args.out_panel
    out_meta = ROOT / args.out_meta
    out_diag = ROOT / args.out_diag

    out_panel.parent.mkdir(parents=True, exist_ok=True)
    out_meta.parent.mkdir(parents=True, exist_ok=True)
    out_diag.parent.mkdir(parents=True, exist_ok=True)

    targets = load_moment_targets(moments_path)

    cfg = SimulationConfig(
        seed=args.seed,
        n_teams=args.n_teams,
        n_weeks=args.n_weeks,
        treatment_effect=args.treatment_effect,
    )

    panel, diag = build_synthetic_panel(targets=targets, cfg=cfg)
    panel.to_csv(out_panel, index=False)

    diag_df = pd.DataFrame(
        [
            {"metric": k, "value": v}
            for k, v in {
                **diag,
                "seed": cfg.seed,
                "n_teams": cfg.n_teams,
                "n_weeks": cfg.n_weeks,
                "latent_treatment_effect": cfg.treatment_effect,
            }.items()
        ]
    )
    diag_df.to_csv(out_diag, index=False)

    metadata = {
        "data_type": "synthetic_calibrated_to_real_proxy_moments",
        "seed": cfg.seed,
        "n_teams": cfg.n_teams,
        "n_weeks": cfg.n_weeks,
        "treatment_effect_latent_units": cfg.treatment_effect,
        "notes": [
            "Synthetic data are calibrated to benchmark moments from a public real-data proxy panel.",
            "Where the proxy panel lacks identifying variation (e.g., no observed adopters), placeholder timing moments are explicitly documented upstream.",
            "Causal interpretation is limited by synthetic design choices and proxy-based benchmarking.",
        ],
        "diagnostics": diag,
    }
    write_json(out_meta, metadata)

    print(f"Wrote {out_panel}")
    print(f"Wrote {out_diag}")
    print(f"Wrote {out_meta}")


if __name__ == "__main__":
    main()
