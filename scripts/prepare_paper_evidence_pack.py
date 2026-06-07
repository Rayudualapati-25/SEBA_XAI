from __future__ import annotations

import csv
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]

STEP3_SUMMARY = ROOT / "prototype/runs/20260527_step3_audit_baselines_seed42/artifacts/audit_detection_summary.csv"
STEP4_SUMMARY = ROOT / "prototype/runs/20260527_step4_permissioned_blockchain_audit_seed42/artifacts/blockchain_detection_summary.csv"
STEP5_OVERHEAD = ROOT / "prototype/runs/20260527_step5_latency_storage_overhead/artifacts/overhead_comparison.csv"
STEP6_COMPARISON = ROOT / "prototype/runs/20260527_step6_experiment_modes_seed42/artifacts/experiment_mode_comparison.csv"
STEP7_METADATA = ROOT / "prototype/runs/20260527_step7_offchain_encrypted_pointers_seed42/artifacts/metadata_leakage_comparison.csv"
STEP7_TAMPER = ROOT / "prototype/runs/20260527_step7_offchain_encrypted_pointers_seed42/artifacts/offchain_tamper_test_results.csv"
STEP8_ABLATION = ROOT / "prototype/runs/20260528_step8_policy_config_ablation_seed42/artifacts/policy_ablation_effects.csv"

TABLE_DIR = ROOT / "results/tables"
PLOT_DIR = ROOT / "results/plots"
PAPER_RESULTS_DIR = ROOT / "papers/final_paper/results"
EXPERIMENT_RUN_DIR = ROOT / "experiments/runs"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def pct(value: str) -> str:
    if value == "":
        return ""
    return f"{float(value) * 100:.1f}%"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def method_interpretation(row: dict[str, str]) -> str:
    method_id = row["method_id"]
    if method_id == "rbac_mutable_log":
        return "Weak baseline for this workload because role/action rules ignore sensitivity, jurisdiction, approval, and privacy context."
    if method_id == "abac_pbac_mutable_log":
        return "Contextual policy decisions match the synthetic oracle, but the mutable log has no internal tamper evidence."
    if method_id == "abac_pbac_signed_hash_chain":
        return "Adds local append-only tamper evidence through hash links and demo signatures."
    if method_id == "abac_pbac_blockchain_style":
        return "Adds permissioned blockchain-style audit commitments without XAI hash logging."
    if method_id == "seba_xai_full":
        return "Proposed mode combining contextual access policy, blockchain-style audit, and XAI explanation-hash logging."
    return "Synthetic experiment method."


def build_method_table() -> list[dict[str, object]]:
    rows = []
    for row in read_csv(STEP6_COMPARISON):
        rows.append(
            {
                "method_id": row["method_id"],
                "method_name": row["method_name"],
                "status": row["status"],
                "decision_model": row["decision_model"],
                "audit_mode": row["audit_mode"],
                "requests": row["requests"],
                "accuracy_vs_policy_oracle": row["accuracy"],
                "false_allow_count": row["false_allow_count"],
                "false_deny_count": row["false_deny_count"],
                "false_escalate_count": row["false_escalate_count"],
                "audit_tamper_detection_rate": row["audit_tamper_detection_rate"],
                "xai_hash_logged": row["xai_hash_logged"],
                "explanation_hash_tamper_detection": row["explanation_hash_tamper_detection"],
                "estimated_total_build_latency_ms_p50": row["estimated_total_build_latency_ms_p50"],
                "storage_bytes_per_event": row["storage_bytes_per_event"],
                "interpretation": method_interpretation(row),
            }
        )
    return rows


def build_tamper_table() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in read_csv(STEP3_SUMMARY):
        design = "mutable_log" if row["log_type"] == "mutable" else "signed_hash_chain"
        rows.append(
            {
                "artifact_layer": "audit_log",
                "design_or_artifact": design,
                "tamper_cases": row["tamper_cases"],
                "detected": row["self_detected"],
                "not_detected": row["self_not_detected"],
                "detection_rate": row["self_detection_rate"],
                "source_artifact": rel(STEP3_SUMMARY),
                "interpretation": "Schema-only mutable logs do not internally detect valid-looking edits."
                if design == "mutable_log"
                else "Signed hash-chain detects the controlled edits in this local test.",
            }
        )
    for row in read_csv(STEP4_SUMMARY):
        rows.append(
            {
                "artifact_layer": "blockchain_audit",
                "design_or_artifact": row["chain_type"],
                "tamper_cases": row["tamper_cases"],
                "detected": row["detected"],
                "not_detected": row["not_detected"],
                "detection_rate": row["detection_rate"],
                "source_artifact": rel(STEP4_SUMMARY),
                "interpretation": "Permissioned blockchain-style blocks detect the controlled block and commitment edits.",
            }
        )

    tamper_rows = [row for row in read_csv(STEP7_TAMPER) if row["expected_tampered"] == "true"]
    by_artifact: dict[str, list[dict[str, str]]] = {}
    for row in tamper_rows:
        by_artifact.setdefault(row["artifact_type"], []).append(row)
    for artifact_type, subset in sorted(by_artifact.items()):
        detected = sum(1 for row in subset if row["verification_detected"] == "true")
        total = len(subset)
        rows.append(
            {
                "artifact_layer": "offchain_storage_pointer",
                "design_or_artifact": artifact_type,
                "tamper_cases": total,
                "detected": detected,
                "not_detected": total - detected,
                "detection_rate": f"{detected / total:.4f}" if total else "0.0000",
                "source_artifact": rel(STEP7_TAMPER),
                "interpretation": "Anchored verification detects the controlled off-chain store or pointer edits.",
            }
        )
    return rows


def build_metadata_table() -> list[dict[str, object]]:
    rows = []
    for row in read_csv(STEP7_METADATA):
        rows.append(
            {
                "ledger_design": row["ledger_design"],
                "events": row["total_events"],
                "columns": row["column_count"],
                "clear_sensitive_columns": row["clear_sensitive_columns"],
                "hashed_or_commitment_columns": row["hashed_or_commitment_columns"],
                "metadata_exposure_score": row["metadata_exposure_score"],
                "decision_visible": row["decision_visible"],
                "purpose_visible": row["purpose_visible"],
                "requester_station_visible": row["requester_station_visible"],
                "target_station_visible": row["target_station_visible"],
                "interpretation": row["interpretation"],
            }
        )
    return rows


def build_latency_table() -> list[dict[str, object]]:
    rows = []
    for row in read_csv(STEP5_OVERHEAD):
        rows.append(
            {
                "component_or_method": row["method"],
                "events_or_requests": row["events_or_requests"],
                "build_or_decision_total_ms_p50": row["build_or_decision_total_ms_p50"],
                "verify_total_ms_p50": row["verify_total_ms_p50"],
                "storage_bytes": row["storage_bytes"],
                "storage_bytes_per_event_or_request": row["storage_bytes_per_event_or_request"],
                "tamper_detection_rate": row["tamper_detection_rate"],
                "scope_note": row["scope_note"],
            }
        )
    return rows


def build_ablation_table() -> list[dict[str, object]]:
    rows = []
    for row in read_csv(STEP8_ABLATION):
        rows.append(
            {
                "method_id": row["method_id"],
                "method_name": row["method_name"],
                "method_type": row["method_type"],
                "disabled_rule_groups": row["disabled_rule_groups"],
                "accuracy_drop_from_full": row["accuracy_drop_from_full"],
                "false_allow_delta_from_full": row["false_allow_delta_from_full"],
                "false_deny_delta_from_full": row["false_deny_delta_from_full"],
                "false_escalate_delta_from_full": row["false_escalate_delta_from_full"],
                "extra_errors_vs_full": row["extra_errors_vs_full"],
                "interpretation": row["interpretation"],
            }
        )
    return rows


def svg_bar_chart(
    path: Path,
    *,
    title: str,
    data: list[tuple[str, float]],
    y_label: str,
    value_suffix: str = "",
    max_value: float | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    width = 980
    height = 480
    left = 190
    right = 36
    top = 68
    bottom = 122
    plot_width = width - left - right
    plot_height = height - top - bottom
    max_data = max((value for _, value in data), default=1.0)
    upper = max_value if max_value is not None else max(max_data * 1.12, 1.0)
    bar_gap = 12
    bar_height = max(18, (plot_height - bar_gap * (len(data) - 1)) / max(len(data), 1))
    palette = ["#2F5D8C", "#3B826B", "#9A6A2F", "#6B5CA5", "#A64B5B", "#4B7F87", "#7C7C3B"]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{left}" y="34" font-family="Arial" font-size="22" font-weight="700" fill="#1f2933">{html.escape(title)}</text>',
        f'<text x="{left}" y="58" font-family="Arial" font-size="13" fill="#52606d">{html.escape(y_label)}</text>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="#9aa5b1" stroke-width="1"/>',
        f'<line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" stroke="#9aa5b1" stroke-width="1"/>',
    ]
    for tick in range(0, 6):
        value = upper * tick / 5
        x = left + (value / upper) * plot_width if upper else left
        parts.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{top + plot_height}" stroke="#edf2f7" stroke-width="1"/>')
        parts.append(f'<text x="{x:.2f}" y="{top + plot_height + 22}" font-family="Arial" font-size="11" text-anchor="middle" fill="#52606d">{value:.1f}{html.escape(value_suffix)}</text>')

    for index, (label, value) in enumerate(data):
        y = top + index * (bar_height + bar_gap)
        bar_width = (value / upper) * plot_width if upper else 0
        color = palette[index % len(palette)]
        parts.append(f'<text x="{left - 10}" y="{y + bar_height * 0.62:.2f}" font-family="Arial" font-size="12" text-anchor="end" fill="#243b53">{html.escape(label)}</text>')
        parts.append(f'<rect x="{left}" y="{y:.2f}" width="{bar_width:.2f}" height="{bar_height:.2f}" rx="3" fill="{color}"/>')
        parts.append(f'<text x="{left + bar_width + 8:.2f}" y="{y + bar_height * 0.62:.2f}" font-family="Arial" font-size="12" fill="#102a43">{value:.3g}{html.escape(value_suffix)}</text>')

    parts.append('<text x="36" y="456" font-family="Arial" font-size="11" fill="#6b7280">Source: generated SEBA-XAI prototype artifacts; synthetic local workload only.</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def md_table(rows: list[dict[str, object]], headers: list[str]) -> str:
    def clean(value: object) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ")

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(clean(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines)


def write_plot_readme(created_at: str, plot_files: list[Path]) -> None:
    lines = [
        "# Plots",
        "",
        f"Generated: {created_at}",
        "",
        "These plots are generated from local synthetic SEBA-XAI prototype artifacts. They are for paper drafting and supervisor review only.",
        "",
        "## Generated Plot Files",
        "",
    ]
    for path in plot_files:
        lines.append(f"- `{rel(path)}`")
    lines.extend(
        [
            "",
            "## Source Data",
            "",
            f"- `{rel(STEP6_COMPARISON)}`",
            f"- `{rel(STEP7_METADATA)}`",
            f"- `{rel(STEP7_TAMPER)}`",
            f"- `{rel(STEP8_ABLATION)}`",
            f"- `{rel(STEP5_OVERHEAD)}`",
            "",
            "## Boundary",
            "",
            "The plots do not show deployment performance, legal compliance, real police data, or production security. They show the current synthetic prototype evidence only.",
        ]
    )
    (PLOT_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_paper_results_readme(created_at: str) -> None:
    PAPER_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    text = f"""# Paper Results Workspace

Generated: {created_at}

This folder contains evidence-safe results text for the SEBA-XAI paper draft.

## Current Result Document

- `experiment_results_narrative.md`

## Writing Boundary

The current results are from a deterministic synthetic workload and local prototype artifacts. They can support a results section about prototype behavior, baseline comparison, ablation, local tamper tests, metadata exposure, and local overhead. They cannot support claims about deployment readiness, legal compliance, real CCTNS/ICJS integration, real police accuracy, or production-grade cryptography.
"""
    (PAPER_RESULTS_DIR / "README.md").write_text(text, encoding="utf-8")


def write_final_paper_readme(created_at: str) -> None:
    text = f"""# Paper Draft Guardrail

Updated: {created_at}

Baseline, proposed-method, and ablation artifacts now exist in the repository, so evidence-backed paper drafting can begin.

Allowed at this stage:

- problem statement;
- related-work notes;
- dataset inventory;
- methodology;
- result tables derived from saved artifacts;
- cautious experiment narrative;
- limitations and failure modes.

Not allowed:

- claims of SOTA;
- deployment claims;
- legal-compliance claims;
- production security claims;
- real police/CCTNS/ICJS performance claims;
- unsupported novelty claims.

Paper text must cite generated artifacts in `results/tables/`, `results/plots/`, `prototype/runs/`, `experiments/runs/`, and `reports/iteration/`.
"""
    (ROOT / "papers/final_paper/README.md").write_text(text, encoding="utf-8")


def write_narrative(
    created_at: str,
    method_rows: list[dict[str, object]],
    tamper_rows: list[dict[str, object]],
    metadata_rows: list[dict[str, object]],
    latency_rows: list[dict[str, object]],
    ablation_rows: list[dict[str, object]],
) -> None:
    rbac = next(row for row in method_rows if row["method_id"] == "rbac_mutable_log")
    seba = next(row for row in method_rows if row["method_id"] == "seba_xai_full")
    full_pbac = next(row for row in ablation_rows if row["method_id"] == "full_configured_pbac")
    sealed = next(row for row in ablation_rows if row["method_id"] == "no_sealed_record_rules")
    privacy = next(row for row in ablation_rows if row["method_id"] == "no_privacy_rules")
    sensitivity = next(row for row in ablation_rows if row["method_id"] == "no_sensitivity_rules")
    mutable = next(row for row in tamper_rows if row["design_or_artifact"] == "mutable_log")
    signed = next(row for row in tamper_rows if row["design_or_artifact"] == "signed_hash_chain")
    chain = next(row for row in tamper_rows if row["design_or_artifact"] == "permissioned_blockchain_style")
    pointer_total = sum(int(row["tamper_cases"]) for row in tamper_rows if row["artifact_layer"] == "offchain_storage_pointer")
    pointer_detected = sum(int(row["detected"]) for row in tamper_rows if row["artifact_layer"] == "offchain_storage_pointer")
    full_meta = next(row for row in metadata_rows if row["ledger_design"] == "full_metadata_ledger")
    min_meta = next(row for row in metadata_rows if row["ledger_design"] == "minimized_commitment_ledger")

    text = f"""# Experiment Results Narrative

Generated: {created_at}

## 1. Experiment Scope

The current SEBA-XAI prototype was evaluated on a deterministic synthetic workload of 1,000 access requests. The workload is not real police data and is not CCTNS/ICJS data. The Step 2 policy oracle is used as the reference label for access decisions. Therefore, the reported accuracy values mean agreement with the synthetic policy oracle, not agreement with real police decisions.

The experiment evidence covers five areas:

- decision behavior of RBAC, ABAC/PBAC, and SEBA-XAI modes;
- tamper detection for mutable logs, signed hash-chain logs, blockchain-style audit blocks, and off-chain pointers;
- metadata exposure in full versus minimized ledger designs;
- local latency and storage overhead;
- policy ablation effects.

## 2. Main Method Comparison

The RBAC mutable-log baseline reached `{rbac['accuracy_vs_policy_oracle']}` accuracy against the synthetic policy oracle, with `{rbac['false_allow_count']}` false allows and `{rbac['false_deny_count']}` false denies. This is expected because the RBAC baseline uses mainly role, action, credential, and purpose. It does not evaluate jurisdiction, sensitivity, privacy flags, approval state, sealed-record status, or fallback review.

The proposed SEBA-XAI mode reached `{seba['accuracy_vs_policy_oracle']}` agreement with the same oracle and had `{seba['false_allow_count']}` false allows in this synthetic run. This should be interpreted carefully: it shows that the configured ABAC/PBAC policy and the SEBA-XAI mode are aligned with the synthetic reference policy. It does not prove real-world correctness.

The full SEBA-XAI row also includes blockchain-style audit and XAI explanation-hash logging. Its local estimated p50 build path is `{seba['estimated_total_build_latency_ms_p50']}` ms for the 1,000-request workload, with `{seba['storage_bytes_per_event']}` bytes per event in the saved audit artifacts. These are local prototype measurements, not deployment performance.

## 3. Audit And Tamper Detection

The mutable log detected `{mutable['detected']}/{mutable['tamper_cases']}` controlled tamper cases by internal self-verification. The signed hash-chain detected `{signed['detected']}/{signed['tamper_cases']}` controlled cases, because changed rows break payload hashes, event links, or demo signatures. The permissioned blockchain-style audit layer detected `{chain['detected']}/{chain['tamper_cases']}` controlled block or commitment tamper cases.

The off-chain storage and pointer layer detected `{pointer_detected}/{pointer_total}` controlled tamper cases. This includes stronger pointer tests where the pointer commitment was recomputed after changing the explanation hash, event commitment, or storage node. Those cases were detected because pointer verification now anchors fields back to Step 2 policy/XAI artifacts and Step 4 block-index artifacts.

These results support a limited claim: the prototype can detect the controlled tamper cases represented in the repository. They do not prove security against compromised keys, malicious quorum validators, production cryptographic attacks, or operational insider misuse.

## 4. Metadata Exposure

The full-metadata ledger view exposes `{full_meta['clear_sensitive_columns']}` clear sensitive/context columns and has a schema-level exposure score of `{full_meta['metadata_exposure_score']}`. The minimized commitment ledger exposes `{min_meta['clear_sensitive_columns']}` clear sensitive/context columns and has a schema-level exposure score of `{min_meta['metadata_exposure_score']}`.

This supports the design choice that raw records and clear operational context should not be placed directly on the audit ledger. The result is only a schema-level exposure comparison. It is not differential privacy, anonymity, or a legal-compliance proof.

## 5. Policy Ablation

The full configured PBAC/ABAC policy is the reference configured method and has `{full_pbac['extra_errors_vs_full']}` extra errors versus itself. Removing sealed-record rules created `{sealed['false_allow_delta_from_full']}` additional false allows and `{sealed['false_escalate_delta_from_full']}` additional false escalations. Removing privacy rules created `{privacy['false_allow_delta_from_full']}` additional false allows. Removing sensitivity rules created `{sensitivity['false_allow_delta_from_full']}` additional false allows and `{sensitivity['false_escalate_delta_from_full']}` additional false escalations.

This supports the argument that the access-control layer should not be reduced to simple RBAC. Sensitive police access decisions require contextual rules for record sensitivity, privacy flags, sealed status, approval, jurisdiction, and assignment.

## 6. What This Proves

- The prototype can generate a reproducible synthetic access-control workload.
- The RBAC baseline is weak against the synthetic policy oracle.
- The ABAC/PBAC policy layer aligns with the synthetic policy oracle in the current run.
- The signed hash-chain and blockchain-style audit layers detect the controlled tamper cases represented in the artifacts.
- The off-chain pointer design can be verified against policy/XAI and blockchain artifacts.
- The minimized ledger design reduces direct metadata exposure at schema level.
- The policy ablation shows which rule groups matter in the synthetic workload.

## 7. What This Does Not Prove

- It does not prove real police decision accuracy.
- It does not prove CCTNS/ICJS deployment readiness.
- It does not prove legal compliance.
- It does not prove production security or privacy.
- It does not prove Hyperledger Fabric performance.
- It does not prove SOTA crime prediction.
- It does not use real FIR, victim, witness, juvenile, or investigation records.

## 8. Paper Use

The safest paper claim is:

> We design and evaluate a synthetic SEBA-XAI prototype for secure, explainable, and auditable inter-agency police-record access governance. The evaluation compares RBAC, ABAC/PBAC, signed hash-chain audit, permissioned blockchain-style audit, off-chain pointer verification, metadata exposure, and policy ablations under a reproducible synthetic workload.

The paper should avoid saying that the system is ready for real policing. It should say that this is a reproducible research prototype and a conservative architecture direction.

## 9. Generated Paper Tables

- `{rel(TABLE_DIR / 'paper_table_01_method_comparison.csv')}`
- `{rel(TABLE_DIR / 'paper_table_02_tamper_detection.csv')}`
- `{rel(TABLE_DIR / 'paper_table_03_metadata_exposure.csv')}`
- `{rel(TABLE_DIR / 'paper_table_04_latency_storage.csv')}`
- `{rel(TABLE_DIR / 'paper_table_05_policy_ablation.csv')}`

## 10. Generated Plots

- `{rel(PLOT_DIR / 'paper_false_allows_by_method.svg')}`
- `{rel(PLOT_DIR / 'paper_tamper_detection_by_design.svg')}`
- `{rel(PLOT_DIR / 'paper_metadata_exposure_score.svg')}`
- `{rel(PLOT_DIR / 'paper_latency_build_verify.svg')}`
- `{rel(PLOT_DIR / 'paper_policy_ablation_false_allows.svg')}`

## Appendix: Compact Tables

### Method Comparison

{md_table(method_rows, ['method_name', 'accuracy_vs_policy_oracle', 'false_allow_count', 'false_deny_count', 'audit_tamper_detection_rate', 'xai_hash_logged'])}

### Tamper Detection

{md_table(tamper_rows, ['artifact_layer', 'design_or_artifact', 'tamper_cases', 'detected', 'detection_rate'])}

### Metadata Exposure

{md_table(metadata_rows, ['ledger_design', 'clear_sensitive_columns', 'metadata_exposure_score', 'decision_visible', 'purpose_visible'])}

### Policy Ablation

{md_table(ablation_rows, ['method_name', 'disabled_rule_groups', 'accuracy_drop_from_full', 'false_allow_delta_from_full', 'false_escalate_delta_from_full'])}
"""
    path = PAPER_RESULTS_DIR / "experiment_results_narrative.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_iteration_report(created_at: str) -> None:
    path = ROOT / "reports/iteration/iter_018_paper_evidence_pack.md"
    text = f"""# Iteration 018: Paper Evidence Pack

Date: 2026-05-28  
Generated at UTC: {created_at}  
Status: paper-ready evidence pack created from existing artifacts

## What Was Done

- Converted Step 3-8 prototype artifacts into curated paper tables.
- Generated SVG plots for false allows, tamper detection, metadata exposure, latency, and policy ablation.
- Wrote an evidence-safe experiment narrative for the paper results section.
- Updated the final-paper guardrail to allow evidence-backed drafting now that baseline, proposed-method, and ablation artifacts exist.

## Generated Tables

```text
results/tables/paper_table_01_method_comparison.csv
results/tables/paper_table_02_tamper_detection.csv
results/tables/paper_table_03_metadata_exposure.csv
results/tables/paper_table_04_latency_storage.csv
results/tables/paper_table_05_policy_ablation.csv
results/tables/paper_evidence_index.csv
```

## Generated Plots

```text
results/plots/paper_false_allows_by_method.svg
results/plots/paper_tamper_detection_by_design.svg
results/plots/paper_metadata_exposure_score.svg
results/plots/paper_latency_build_verify.svg
results/plots/paper_policy_ablation_false_allows.svg
```

## Generated Paper Text

```text
papers/final_paper/results/README.md
papers/final_paper/results/experiment_results_narrative.md
```

## Evidence Boundary

The generated material is suitable for a prototype-results section. It is not evidence of deployment readiness, legal compliance, real police accuracy, real CCTNS/ICJS integration, production cryptography, or SOTA crime prediction.

## Next Step

Use the narrative and tables to write the formal IEEE Results and Discussion sections, then create a short supervisor-facing slide deck.
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    PAPER_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    EXPERIMENT_RUN_DIR.mkdir(parents=True, exist_ok=True)

    method_rows = build_method_table()
    tamper_rows = build_tamper_table()
    metadata_rows = build_metadata_table()
    latency_rows = build_latency_table()
    ablation_rows = build_ablation_table()

    table_specs = [
        ("paper_table_01_method_comparison.csv", method_rows, list(method_rows[0].keys()), "Baseline/proposed method comparison from Step 6."),
        ("paper_table_02_tamper_detection.csv", tamper_rows, list(tamper_rows[0].keys()), "Controlled tamper detection from Step 3, Step 4, and Step 7."),
        ("paper_table_03_metadata_exposure.csv", metadata_rows, list(metadata_rows[0].keys()), "Full metadata versus minimized commitment ledger exposure from Step 7."),
        ("paper_table_04_latency_storage.csv", latency_rows, list(latency_rows[0].keys()), "Local latency and storage overhead from Step 5."),
        ("paper_table_05_policy_ablation.csv", ablation_rows, list(ablation_rows[0].keys()), "Policy ablation effects from Step 8."),
    ]
    for filename, rows, fieldnames, _ in table_specs:
        write_csv(TABLE_DIR / filename, rows, fieldnames)

    evidence_index = [
        {
            "artifact": filename,
            "type": "paper_table",
            "source": note,
            "path": rel(TABLE_DIR / filename),
        }
        for filename, _, _, note in table_specs
    ]
    write_csv(TABLE_DIR / "paper_evidence_index.csv", evidence_index, ["artifact", "type", "source", "path"])

    plot_files = [
        PLOT_DIR / "paper_false_allows_by_method.svg",
        PLOT_DIR / "paper_tamper_detection_by_design.svg",
        PLOT_DIR / "paper_metadata_exposure_score.svg",
        PLOT_DIR / "paper_latency_build_verify.svg",
        PLOT_DIR / "paper_policy_ablation_false_allows.svg",
    ]
    svg_bar_chart(
        plot_files[0],
        title="False Allows by Method",
        y_label="Count of requests allowed when policy oracle did not allow",
        data=[(str(row["method_name"])[:42], float(row["false_allow_count"])) for row in method_rows],
    )
    svg_bar_chart(
        plot_files[1],
        title="Controlled Tamper Detection by Design",
        y_label="Detection rate in local controlled tamper tests",
        data=[(str(row["design_or_artifact"])[:42], float(row["detection_rate"]) * 100) for row in tamper_rows],
        value_suffix="%",
        max_value=100,
    )
    svg_bar_chart(
        plot_files[2],
        title="Schema-Level Metadata Exposure",
        y_label="Exposure score; lower is better",
        data=[(str(row["ledger_design"])[:42], float(row["metadata_exposure_score"])) for row in metadata_rows],
        max_value=1.0,
    )
    svg_bar_chart(
        plot_files[3],
        title="Local Build/Decision Latency p50",
        y_label="p50 milliseconds for local prototype artifact generation",
        data=[(str(row["component_or_method"])[:42], float(row["build_or_decision_total_ms_p50"] or 0)) for row in latency_rows],
    )
    svg_bar_chart(
        plot_files[4],
        title="Policy Ablation: Extra False Allows",
        y_label="False allows added compared with full configured PBAC/ABAC",
        data=[(str(row["method_name"]).replace("Ablation: ", "")[:42], float(row["false_allow_delta_from_full"])) for row in ablation_rows],
    )

    write_plot_readme(created_at, plot_files)
    write_paper_results_readme(created_at)
    write_final_paper_readme(created_at)
    write_narrative(created_at, method_rows, tamper_rows, metadata_rows, latency_rows, ablation_rows)
    write_iteration_report(created_at)

    experiment_record = {
        "run_id": "20260528_paper_evidence_pack",
        "created_at_utc": created_at,
        "artifact_type": "paper_evidence_pack",
        "result_claim": "derived paper tables, plots, and narrative from saved synthetic prototype artifacts",
        "source_artifacts": [
            rel(STEP3_SUMMARY),
            rel(STEP4_SUMMARY),
            rel(STEP5_OVERHEAD),
            rel(STEP6_COMPARISON),
            rel(STEP7_METADATA),
            rel(STEP7_TAMPER),
            rel(STEP8_ABLATION),
        ],
        "generated_tables": [rel(TABLE_DIR / filename) for filename, _, _, _ in table_specs],
        "generated_plots": [rel(path) for path in plot_files],
        "generated_text": [
            rel(PAPER_RESULTS_DIR / "README.md"),
            rel(PAPER_RESULTS_DIR / "experiment_results_narrative.md"),
            "reports/iteration/iter_018_paper_evidence_pack.md",
        ],
        "limitations": [
            "Derived from synthetic local prototype artifacts only.",
            "No real police data, CCTNS data, ICJS data, FIR text, victim record, witness record, or juvenile record is used.",
            "No production cryptography, legal compliance proof, or deployment benchmark is claimed.",
        ],
    }
    write_json(EXPERIMENT_RUN_DIR / "20260528_paper_evidence_pack.json", experiment_record)

    print("Wrote paper evidence pack")
    print(f"Tables: {TABLE_DIR}")
    print(f"Plots: {PLOT_DIR}")
    print(f"Narrative: {PAPER_RESULTS_DIR / 'experiment_results_narrative.md'}")


if __name__ == "__main__":
    main()
