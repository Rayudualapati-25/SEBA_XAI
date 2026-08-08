# Latency And Storage Overhead Data Dictionary

This file describes Step 5 outputs.

## Important Boundary

These measurements are local prototype measurements on the current machine. They are useful for comparing prototype components, but they are not deployment or Hyperledger Fabric benchmarks.

## Core Files

- `latency_summary.csv`: p50/p95/p99 timing summary for each component.
- `latency_samples.csv`: per-request/per-event/per-block sample timings.
- `storage_overhead.csv`: file-size overhead of generated artifacts.
- `overhead_comparison.csv`: compact comparison table for paper notes.

## Important Metrics

| Field | Meaning |
|---|---|
| `total_ms_p50` | Median total time across repeated aggregate runs, or median sample latency for per-unit operations. |
| `ms_per_unit_p50` | Median total divided by count for aggregate operations, or median sample latency for per-unit operations. |
| `throughput_units_per_sec_p50` | Approximate local throughput from median timing. |
| `bytes_per_event_or_request` | Storage size divided by request/event count. |

## Correct Interpretation

Use these numbers as local overhead evidence only. Do not describe them as real police-system performance or blockchain-network performance.
