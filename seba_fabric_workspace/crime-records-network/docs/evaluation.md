# Evaluation status

## Verified on 2026-08-11

| Check | Actual result | Scope |
|---|---:|---|
| Chaincode unit/contract suite | 92 passing | mock Fabric state; 94.15% statements, 87.37% branches |
| Backend live suite | 33 passing | real local Fabric identities, peers, API and vault |
| Smoke suite | 16 passing | eight policy scenarios plus integrity/custody/audit flows |
| Direct-ledger audit check | 116 events returned in that run | live ledger read; count changes as the app is used |

Coverage is execution coverage, not proof of correctness or security.

## Baseline and ablation

`experiments/measure.js` removes credential state, assignment, jurisdiction,
protection flags, purpose, and approval, leaving a role-only view permission.
It compares that ablation to the deployed contextual policy on the fixed eight
synthetic scenarios.

The recorded run in
`experiments/results/seba_xai_contextual_run_2026-08-11T15-22-52-298Z.json`
produced:

| Method | Correct outcomes on the fixed workload |
|---|---:|
| Role-only ablation | 1/8 |
| Contextual Fabric policy | 8/8 |

This is a deterministic functional scenario result, not evidence of real-world
accuracy, fairness, or operational effectiveness. The baseline is an ablation,
not a published competing model.

The same run recorded that a forged explanation was detected, raw synthetic
victim content was absent from ledger metadata, and the metadata contained a
SHA-256 commitment.

## Latency interpretation

In that single-host run, decision commits were approximately 2.01–2.09 seconds.
The network's configured orderer `BatchTimeout` is two seconds, so these numbers
are dominated by waiting for block formation. They include REST, Gateway,
endorsement, ordering and commit observation. They are not multi-site benchmarks
and should not be compared as pure policy-computation time.

## Reproduce

```bash
make down
make all
make backend          # terminal 1

make test             # terminal 2
make smoke
make verify-log
make measure
```

Each new measurement uses timestamped result files and therefore does not
overwrite earlier artifacts.

## Limitations

- synthetic cases and self-defined policy fixtures;
- one computer, one orderer, and local containers;
- server-held development private keys;
- filesystem vault without at-rest encryption or HSM/KMS;
- no real CCTNS/ICJS integration or personal data;
- no claim of production readiness, legal compliance, or security guarantee.
