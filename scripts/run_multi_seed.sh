#!/usr/bin/env bash
# Multi-seed reproduction driver for SEBA-XAI Steps 1-4.
#
# Runs the four new seeds (7, 21, 99, 123). Seed 42 already exists from
# earlier work and is reused as-is. The aggregation script in Python then
# pulls all five seeds together.

set -euo pipefail

cd "$(dirname "$0")/.."

PY=${PY:-python3}
DATE=20260528
SEEDS=(7 21 99 123)

for SEED in "${SEEDS[@]}"; do
  echo "===== seed=${SEED} ====="

  STEP1="${DATE}_step1_synthetic_requests_seed${SEED}"
  STEP2="${DATE}_step2_policy_oracle_seed${SEED}"
  STEP3="${DATE}_step3_audit_baselines_seed${SEED}"
  STEP4="${DATE}_step4_permissioned_blockchain_audit_seed${SEED}"

  "$PY" prototype/synthetic_access_sim/generate_synthetic_requests.py \
    --run-id "$STEP1" --seed "$SEED" --num-requests 1000

  "$PY" prototype/synthetic_access_sim/policy_oracle.py \
    --input-run-id "$STEP1" --run-id "$STEP2"

  "$PY" prototype/synthetic_access_sim/audit_baseline.py \
    --input-run-id "$STEP2" --run-id "$STEP3"

  "$PY" prototype/synthetic_access_sim/blockchain_audit.py \
    --input-run-id "$STEP3" --run-id "$STEP4"
done

echo "All seeds complete."
