#!/usr/bin/env python3
"""Generate explanation and audit quality metrics for SEBA-XAI.

Outputs:
    results/tables/explanation_audit_quality.csv
    results/tables/explanation_audit_quality_summary.csv
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from seba.scoring.grid import OUT_DIR, RUNS_DIR, discover_seeds
from seba.xai_quality import evaluate_seed, summarize_quality

STEP3_RE = re.compile(r"^(?P<date>\d{8})_step3_audit_baselines_seed(?P<seed>\d+)$")


def _step4_artifacts_for(signed_log_csv: Path) -> tuple[Path, Path]:
    step3_dir = signed_log_csv.parents[1]
    match = STEP3_RE.match(step3_dir.name)
    if not match:
        raise ValueError(f"unexpected signed-log path: {signed_log_csv}")
    seed = int(match["seed"])
    date = match["date"]
    step4_dir = (
        RUNS_DIR
        / f"{date}_step4_permissioned_blockchain_audit_seed{seed}"
        / "artifacts"
    )
    block_index = step4_dir / "block_event_index.csv"
    blocks = step4_dir / "permissioned_audit_blocks.jsonl"
    if not block_index.exists() or not blocks.exists():
        raise FileNotFoundError(f"missing step-4 artifacts for seed {seed}: {step4_dir}")
    return block_index, blocks


def run(out_dir: Path = OUT_DIR) -> dict[str, Path]:
    rows: list[dict[str, float | int]] = []
    for assets in discover_seeds():
        block_index, blocks = _step4_artifacts_for(assets.signed_log_csv)
        rows.append(
            evaluate_seed(
                seed=assets.seed,
                labeled_requests_csv=assets.labeled_requests_csv,
                signed_log_csv=assets.signed_log_csv,
                block_index_csv=block_index,
                blocks_jsonl=blocks,
            )
        )

    if not rows:
        raise RuntimeError("No seed assets found. Run scripts/run_multi_seed.sh first.")

    out_dir.mkdir(parents=True, exist_ok=True)
    per_seed = pd.DataFrame(rows).sort_values("seed")
    summary = summarize_quality(per_seed)

    per_seed_path = out_dir / "explanation_audit_quality.csv"
    summary_path = out_dir / "explanation_audit_quality_summary.csv"
    per_seed.to_csv(per_seed_path, index=False)
    summary.to_csv(summary_path, index=False)
    return {"per_seed": per_seed_path, "summary": summary_path}


def main() -> None:
    outputs = run()
    print(f"wrote {outputs['per_seed']}")
    print(f"wrote {outputs['summary']}")


if __name__ == "__main__":
    main()
