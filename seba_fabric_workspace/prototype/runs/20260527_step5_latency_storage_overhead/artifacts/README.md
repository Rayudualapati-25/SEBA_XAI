# Run 20260527_step5_latency_storage_overhead

Purpose: Step 5 local latency and storage-overhead measurement.

Requests measured: `1000`

Audit events measured: `1000`

Blocks measured: `20`

## What This Run Contains

- latency summary table;
- per-request decision latency samples;
- signed-event latency samples;
- block-creation latency samples;
- storage overhead table;
- comparison table across policy/XAI, mutable log, signed hash-chain, and blockchain-style audit.

## What This Run Does Not Claim

- No deployment performance claim.
- No network consensus benchmark.
- No Hyperledger Fabric benchmark.
- No real police/CCTNS/ICJS/FIR data.

## Reproduce

```bash
python3 prototype/synthetic_access_sim/measure_overhead.py \
  --run-id 20260527_step5_latency_storage_overhead
```
