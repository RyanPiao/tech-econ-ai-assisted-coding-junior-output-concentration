from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_moment_targets(path: Path) -> dict[str, float]:
    df = pd.read_csv(path)
    required = {"moment", "target_value"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Moment file missing required columns: {missing}")
    return {row["moment"]: float(row["target_value"]) for _, row in df.iterrows()}
