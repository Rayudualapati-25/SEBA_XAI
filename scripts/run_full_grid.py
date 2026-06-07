#!/usr/bin/env python3
"""Run the full SEBA-XAI evaluation grid: every defense × attack × seed.

Outputs three CSVs under results/tables/:
    full_grid_raw.csv          one row per (seed, defense, attack)
    full_grid_per_attack.csv   aggregated per (defense, attack)
    full_grid_aas_by_defense.csv  AAS mean/std per defense across seeds
"""

from __future__ import annotations

import sys

from seba.scoring.grid import run_grid


def main() -> int:
    paths = run_grid()
    for label, path in paths.items():
        print(f"{label:14s} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
