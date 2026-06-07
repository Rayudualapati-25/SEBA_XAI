# Iteration 009: Synthetic Access-Request Generator

Date: 2026-05-27  
Status: Step 1 implementation complete  
Scope: synthetic workload generation only

## What Was Done

Implemented the first runnable artifact for the SEBA-XAI research implementation:

- added `prototype/synthetic_access_sim/generate_synthetic_requests.py`;
- added `prototype/synthetic_access_sim/README.md`;
- generated run record `prototype/runs/20260527_step1_synthetic_requests_seed42/`;
- saved dataset profile table to `prototype/results/tables/synthetic_request_step1_profile.csv`;
- updated `experiments/runs/README.md`.

## Generated Artifacts

Run folder:

```text
prototype/runs/20260527_step1_synthetic_requests_seed42/
  config.yaml
  logs/generation.log
  metrics.json
  artifacts/
    README.md
    stations.csv
    officers.csv
    cases.csv
    records.csv
    access_requests.csv
    dataset_manifest.json
    data_dictionary.md
    dataset_profile.csv
```

## Dataset Profile

The run generated:

| Artifact | Count |
|---|---:|
| synthetic officers | 240 |
| synthetic cases | 360 |
| synthetic records | 900 |
| synthetic access requests | 1000 |

All access-request rows are marked:

- `synthetic_only=true`;
- `raw_record_included=false`.

The 1000 requests cover all planned scenario types:

- normal in-jurisdiction request;
- cross-jurisdiction sensitive request;
- revoked credential;
- stale case assignment;
- juvenile-sensitive request;
- emergency override;
- court/prosecution request;
- sealed record request;
- expired approval token;
- random context.

## Validation

Validation performed:

- Python syntax check passed with `python3 -m py_compile`;
- request row count matched `metrics.json`;
- all request rows were synthetic;
- no request row included raw record content;
- all 10 scenario types were present.

## What Worked

- The generator is deterministic through a fixed seed.
- The output follows the repository run-record structure.
- The workload contains subject, object, action, environment, jurisdiction, approval, and sensitivity attributes needed for RBAC/ABAC/PBAC testing.
- The run creates file hashes in `dataset_manifest.json` for traceability.

## What Is Weak Or Missing

- No access-control decision has been implemented yet.
- No baseline comparison has been run.
- No blockchain audit layer has been implemented yet.
- No XAI explanation artifact has been generated yet.
- Scenario labels are workload-coverage labels only; they are not model labels or results.

## Next Step

Implement the deterministic policy oracle.

The oracle should read `access_requests.csv` and output:

- decision: `allow`, `deny`, or `escalate`;
- reason code;
- decisive attributes;
- failed policy conditions;
- required approval condition where applicable;
- policy version.

This oracle is required before RBAC, ABAC/PBAC, blockchain audit, or XAI experiments can be measured honestly.
