# 09 Evaluation Metrics

Generated: 2026-05-12

## Metric Philosophy

The paper should evaluate the system on what it actually claims: secure, explainable, auditable access governance. Accuracy alone is not enough. Blockchain latency alone is not enough. XAI visualizations alone are not enough.

## Access-Control Metrics

- **Authorization accuracy:** fraction of requests matching the policy oracle.
- **False allow rate:** denied/escalated requests incorrectly allowed. This is the highest-risk error.
- **False deny rate:** legitimate requests incorrectly denied.
- **False escalation rate:** requests unnecessarily sent to superior review.
- **Escalation precision:** fraction of escalations that truly required superior approval.
- **Policy coverage:** fraction of requests for which the policy engine can provide a deterministic reason.
- **Reason-code completeness:** fraction of decisions with machine-readable reason codes.

## Security and Audit Metrics

- **Audit completeness:** fraction of required events present for request reconstruction.
- **Audit reconstruction success:** fraction of decisions reconstructable from stored request, policy, model, explanation, and approval artifacts.
- **Tamper detection rate:** fraction of injected tampering cases detected.
- **False tamper alert rate:** benign cases incorrectly flagged.
- **Hash verification success:** fraction of explanation/payload/policy hashes that verify.
- **Revocation delay:** time between credential revocation and denied access.
- **Policy-update consistency:** fraction of nodes enforcing the intended policy version.
- **Replay resistance:** fraction of replayed approval tokens rejected.

## Blockchain/System Metrics

- **Decision latency p50/p95/p99:** request submit to allow/deny/escalate decision.
- **Audit write latency p50/p95/p99:** decision to committed audit event.
- **Throughput:** completed requests per second.
- **Approval workflow latency:** request to final human approval/denial.
- **Storage overhead per request:** ledger bytes plus off-chain artifacts.
- **Failed transaction rate:** rejected or failed audit writes under load.
- **Outage behavior:** decisions preserved, delayed, or failed during node/partition simulation.

## Privacy and Metadata-Leakage Metrics

- **Metadata leakage score:** weighted exposure of station pair, role/rank, sensitivity, case type, timing, and approval pattern.
- **Sensitive-attribute inference accuracy:** attacker's ability to infer hidden sensitivity/case type from audit metadata.
- **Identifier exposure count:** number of direct identifiers visible in audit events.
- **Payload exposure rate:** fraction of raw sensitive records leaked to unauthorized components.
- **Explanation leakage flag:** whether explanation text reveals protected or classified attributes.
- **Audit utility after minimization:** reconstruction success after metadata reduction.

Important: these are empirical/privacy-risk metrics, not formal privacy proofs.

## XAI Metrics

- **Explanation completeness:** required fields present: decision, decisive attributes, missing attributes, policy version, model version, confidence/risk if applicable.
- **Explanation fidelity:** agreement between explanation and actual model/policy decision logic.
- **Explanation stability:** consistency under small non-sensitive perturbations.
- **Role coverage:** whether officer, superior, auditor, and court/prosecutor views are available.
- **Human override traceability:** whether override reason and responsible reviewer are recorded.
- **Explanation verification:** whether stored explanation hash matches the artifact.

## Aggregate Crime Modeling Metrics

Use only for NCRB/BPRD aggregate experiments:

- **MAE/RMSE:** count or rate prediction error.
- **Poisson deviance:** for count models where suitable.
- **Temporal holdout error:** performance on later years held out from training.
- **Per-state/per-region error:** geographic error distribution.
- **Calibration:** if risk buckets are used.
- **Feature stability:** whether important features change sharply across folds/years.
- **Explanation stability:** whether explanations are robust across nearby years or comparable regions.

## Fairness and Bias Diagnostics

Use with caution because public aggregate data may not support individual fairness claims.

- error by state/UT or region;
- error by urban/rural or police-resource strata if data supports it;
- false allow/deny by officer role/rank and record sensitivity in synthetic workload;
- disparate escalation rates across simulated station/district groups;
- sensitivity analysis for reporting-intensity proxies.

Do not claim fairness in Indian policing from synthetic data alone.

## Tables Required in the Paper

1. Dataset suitability table.
2. Literature gap table.
3. Architecture component table.
4. Baseline versus proposed-method comparison.
5. Ablation table.
6. Threat-case/tamper-detection table.
7. Latency/throughput table.
8. XAI artifact completeness table.
9. Limitations table.

## Minimum Acceptance Criteria

The first complete experimental paper must show:

- false allow rate for each design;
- audit completeness for each design;
- tamper detection under injected attacks;
- latency/throughput overhead;
- at least five ablations;
- at least one negative or trade-off result;
- clear statement that no real police data was used unless official access is obtained.
