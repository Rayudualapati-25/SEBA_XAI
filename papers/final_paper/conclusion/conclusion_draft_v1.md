# Conclusion (Draft v1)

Status: draft text for the SEBA-XAI paper. Not final camera-ready prose.
Evidence basis: `CONTRIBUTION.md`, `results/FINDINGS.md`,
`papers/final_paper/results/results_draft_v1.md`, and
`papers/final_paper/limitations/limitations_draft_v1.md`.

## Conclusion

This paper frames SEBA-XAI as a CCTNS/ICJS-compatible research prototype for
explainable, blockchain-audited access governance over sensitive police and
criminal-justice records. The work does not replace existing systems and does
not put raw records on-chain. Instead, it studies a controlled overlay in which
synthetic access requests are evaluated by a declared policy oracle, recorded
through signed and blockchain-style audit commitments, and reviewed through
structured explanation artifacts.

The main evidence-backed result is narrow but useful. In the synthetic
benchmark, ordinary ledger and ABAC-style defenses are stronger than NS-PI for
ordinary tamper attacks, while the trusted raw-attribute policy oracle is the
strongest overall baseline. However, for the validly re-signed
`compromised_signer` attack, ledger-only and audit-only baselines are blind by
construction, while both NS-PI and the trusted oracle detect the corruption
across the five full-grid seeds (`results/tables/seed_confidence_summary.csv`,
`papers/final_paper/results/results_draft_v1.md` Section 4). This supports
framing NS-PI as a complementary log-only policy-drift signal, not as a
replacement for cryptographic audit or trusted policy re-evaluation.

The evaluation also makes the XAI layer measurable. Structured traces,
counterfactual coverage, duplicate-context stability, and audit reconstruction
are complete across the evaluated seeds, while decisive-attribute full text
coverage remains imperfect at mean 0.781000/std 0.020833
(`results/tables/explanation_audit_quality_summary.csv`,
`papers/final_paper/results/results_draft_v1.md` Section 7). This distinction
is important: the prototype can reconstruct and audit structured explanation
artifacts, but the natural-language rendering still needs improvement.

The limitations define the boundary of the contribution. All results come from
synthetic workloads. NS-PI misses 2% and 5% global compromised-signer corruption
and misses 10% targeted station/district corruption in the current benchmark.
Low-rate detection is workload-size dependent even after extending the workload
stress matrix to five seeds. These weaknesses are not side notes; they are part
of the research result because they show where a log-only drift detector is
useful and where a stronger independent policy view is still needed.

The final claim is therefore conservative: SEBA-XAI shows how permissioned
audit commitments, contextual access control, trusted policy re-evaluation, and
interpretable drift monitoring can be evaluated together for sensitive
inter-agency access governance. The current prototype provides a reproducible
benchmark and paper-ready evidence for that claim, while leaving operational
integration, formal privacy analysis, and domain-validated policy rules as
future work.
