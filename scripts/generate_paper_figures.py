#!/usr/bin/env python3
"""Generate paper-facing SVG figures from existing SEBA-XAI artifacts.

The figures are intentionally conservative:
- all quantitative plots read from ``results/tables``;
- architecture figures describe the prototype boundary, not deployment;
- captions and interpretation remain in Markdown drafts, not embedded as claims.
"""

from __future__ import annotations

import os
from pathlib import Path

MPLCONFIGDIR = Path("/private/tmp/seba_xai_mplconfig")
MPLCONFIGDIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIGDIR))
XDG_CACHE_HOME = Path("/private/tmp/seba_xai_xdg_cache")
XDG_CACHE_HOME.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("XDG_CACHE_HOME", str(XDG_CACHE_HOME))

import matplotlib  # noqa: E402

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
TABLES = REPO_ROOT / "results" / "tables"
OUT = REPO_ROOT / "papers" / "final_paper" / "figures_tables"

COLORS = {
    "navy": "#2f3a4a",
    "blue": "#4f81bd",
    "green": "#70ad47",
    "orange": "#f4b183",
    "red": "#c00000",
    "gray": "#bfbfbf",
    "light_blue": "#d9eaf7",
    "light_green": "#e2f0d9",
    "light_orange": "#fde9d9",
    "light_gray": "#f2f2f2",
}


def setup() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "figure.dpi": 160,
            "savefig.dpi": 160,
        }
    )


def save(fig: plt.Figure, filename: str) -> None:
    fig.savefig(OUT / filename, format="svg", bbox_inches="tight")
    plt.close(fig)


def box(ax: plt.Axes, x: float, y: float, w: float, h: float, text: str, fc: str) -> None:
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.03,rounding_size=0.04",
        linewidth=1.1,
        edgecolor=COLORS["navy"],
        facecolor=fc,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", wrap=True)


def arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float]) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=10,
            linewidth=1.0,
            color=COLORS["navy"],
        )
    )


def figure_architecture() -> None:
    fig, ax = plt.subplots(figsize=(11.0, 5.8))
    ax.set_axis_off()
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)

    box(
        ax,
        0.3,
        4.9,
        2.1,
        0.8,
        "Existing agency\nrecord systems\n(raw records off-chain)",
        COLORS["light_gray"],
    )
    box(
        ax,
        3.0,
        4.9,
        2.0,
        0.8,
        "Access request\ngateway\nS/O/A/E attributes",
        COLORS["light_blue"],
    )
    box(
        ax,
        5.7,
        4.9,
        2.0,
        0.8,
        "Policy oracle\nRBAC + ABAC/PBAC",
        COLORS["light_green"],
    )
    box(
        ax,
        8.3,
        5.7,
        1.8,
        0.8,
        "Decision\nallow / deny /\nescalate",
        COLORS["light_green"],
    )
    box(
        ax,
        8.3,
        4.2,
        1.8,
        0.8,
        "XAI artifacts\nreasons + traces +\ncounterfactuals",
        COLORS["light_orange"],
    )
    box(ax, 10.5, 4.9, 1.2, 0.8, "Audit event\nbuilder", COLORS["light_blue"])

    box(
        ax,
        3.1,
        2.4,
        2.4,
        0.9,
        "Off-chain encrypted\nrecords and artifacts\n(pointers + hashes)",
        COLORS["light_gray"],
    )
    box(
        ax,
        6.1,
        2.4,
        2.3,
        0.9,
        "Permissioned audit\nsimulation\nhash chain + blocks",
        COLORS["light_blue"],
    )
    box(
        ax,
        9.0,
        2.4,
        2.1,
        0.9,
        "Auditor review\nverify commitments\nreconstruct event",
        COLORS["light_green"],
    )
    box(ax, 6.1, 0.8, 2.3, 0.9, "NS-PI drift detector\nlog-only signal", COLORS["light_orange"])
    box(
        ax,
        9.0,
        0.8,
        2.1,
        0.9,
        "Trusted policy oracle\nindependent request view",
        COLORS["light_orange"],
    )

    arrow(ax, (2.4, 5.3), (3.0, 5.3))
    arrow(ax, (5.0, 5.3), (5.7, 5.3))
    arrow(ax, (7.7, 5.3), (8.3, 6.1))
    arrow(ax, (7.7, 5.3), (8.3, 4.6))
    arrow(ax, (10.1, 6.1), (10.5, 5.5))
    arrow(ax, (10.1, 4.6), (10.5, 5.1))
    arrow(ax, (11.1, 4.9), (7.3, 3.3))
    arrow(ax, (11.1, 4.9), (4.3, 3.3))
    arrow(ax, (8.4, 2.9), (9.0, 2.9))
    arrow(ax, (7.2, 2.4), (7.2, 1.7))
    arrow(ax, (7.7, 5.0), (10.0, 1.7))

    ax.set_title("SEBA-XAI overlay: records stay off-chain, audit stores commitments")
    save(fig, "fig_01_seba_xai_architecture.svg")


def figure_visibility() -> None:
    fig, ax = plt.subplots(figsize=(10.6, 5.2))
    ax.set_axis_off()
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)

    box(ax, 0.5, 3.7, 2.0, 0.9, "Original synthetic\nrequest attributes", COLORS["light_gray"])
    box(ax, 3.3, 3.7, 2.0, 0.9, "Declared policy\noracle", COLORS["light_green"])
    box(ax, 6.1, 3.7, 2.0, 0.9, "Signed canonical\ndecision log", COLORS["light_blue"])
    box(ax, 9.0, 4.8, 2.1, 0.8, "Ledger / CT /\nsigned-chain checks", COLORS["light_blue"])
    box(ax, 9.0, 3.4, 2.1, 0.8, "ABAC/Fabric-style\nre-execution", COLORS["light_green"])
    box(ax, 9.0, 2.0, 2.1, 0.8, "NS-PI\nlog-only drift", COLORS["light_orange"])
    box(ax, 6.1, 0.8, 2.3, 0.8, "Trusted raw-attribute\npolicy oracle", COLORS["light_orange"])
    box(ax, 3.0, 1.6, 2.4, 0.8, "Compromised signer\nflips decisions and\nre-signs log", "#f8d7da")

    arrow(ax, (2.5, 4.15), (3.3, 4.15))
    arrow(ax, (5.3, 4.15), (6.1, 4.15))
    arrow(ax, (8.1, 4.15), (9.0, 5.2))
    arrow(ax, (8.1, 4.15), (9.0, 3.8))
    arrow(ax, (8.1, 4.15), (9.0, 2.4))
    arrow(ax, (2.5, 3.9), (6.1, 1.2))
    arrow(ax, (4.2, 2.4), (6.1, 3.9))

    ax.text(
        0.6,
        0.25,
        "Key boundary: ledger-style baselines see the recorded signed log; "
        "the trusted oracle assumes an independent request view.",
        ha="left",
        va="bottom",
        fontsize=8,
    )
    ax.set_title("Detector visibility in the compromised-signer threat model")
    save(fig, "fig_02_detector_visibility.svg")


def figure_compromised_signer() -> None:
    conf = pd.read_csv(TABLES / "seed_confidence_summary.csv")
    rows = conf[
        (conf["metric_family"] == "detection_compromised_signer")
        & (conf["metric"] == "detection_rate")
    ].copy()
    baseline_defs = {
        "signed_chain",
        "blockchain_style",
        "ct_log",
        "fabric_abac",
        "abac_reexec",
        "mutable_log",
    }
    baseline_mean = rows[rows["group"].str.replace("defense=", "").isin(baseline_defs)][
        "mean"
    ].mean()
    nspi = float(rows[rows["group"] == "defense=nspi_drift"]["mean"].iloc[0])
    oracle = float(rows[rows["group"] == "defense=trusted_policy_oracle"]["mean"].iloc[0])

    labels = ["Ledger/ABAC\nbaselines", "NS-PI\nlog-only drift", "Trusted\npolicy oracle"]
    values = [baseline_mean, nspi, oracle]
    colors = [COLORS["gray"], COLORS["orange"], COLORS["green"]]

    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    bars = ax.bar(labels, values, color=colors, edgecolor=COLORS["navy"], linewidth=0.8)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("Detection rate")
    ax.set_title("Compromised-signer detection across five seeds")
    ax.grid(axis="y", alpha=0.25)
    for bar, value in zip(bars, values, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.035,
            f"{value:.1f}",
            ha="center",
            va="bottom",
        )
    ax.text(
        0.0,
        -0.24,
        "Source: results/tables/seed_confidence_summary.csv. Synthetic benchmark only.",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8,
    )
    save(fig, "fig_03_compromised_signer_detection.svg")


def figure_sensitivity() -> None:
    sens = pd.read_csv(TABLES / "nspi_compromised_signer_sensitivity_summary.csv")
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    x = sens["flip_fraction_requested"] * 100
    ax.plot(x, sens["nspi_global_detection_rate"], marker="o", label="NS-PI global")
    ax.plot(x, sens["nspi_per_station_detection_rate"], marker="s", label="NS-PI per-station")
    ax.plot(x, sens["trusted_oracle_detection_rate"], marker="^", label="Trusted oracle")
    ax.set_ylim(-0.05, 1.08)
    ax.set_xlabel("Global decision flip fraction (%)")
    ax.set_ylabel("Detection rate")
    ax.set_title("NS-PI sensitivity to compromised-signer corruption rate")
    ax.grid(alpha=0.25)
    ax.legend(loc="lower right")
    ax.text(
        0.0,
        -0.26,
        "Source: results/tables/nspi_compromised_signer_sensitivity_summary.csv.",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8,
    )
    save(fig, "fig_04_nspi_sensitivity.svg")


def figure_xai_quality() -> None:
    quality = pd.read_csv(TABLES / "explanation_audit_quality_summary.csv")
    wanted = [
        ("trace_complete_rate", "Trace\ncomplete"),
        ("counterfactual_coverage_rate", "Counterfactual\ncoverage"),
        ("counterfactual_validity_rate", "Counterfactual\nvalidity"),
        ("stable_decision_reason_row_rate", "Stable decision\nand reason"),
        ("audit_reconstruction_rate", "Audit\nreconstruction"),
        ("decisive_attribute_full_text_coverage_rate", "Full decisive\nattribute text"),
    ]
    data = quality.set_index("metric").loc[[w[0] for w in wanted]]
    labels = [w[1] for w in wanted]
    means = data["mean"].astype(float).to_numpy()
    stds = data["std"].astype(float).to_numpy()

    fig, ax = plt.subplots(figsize=(8.2, 4.2))
    bars = ax.bar(
        labels,
        means,
        yerr=stds,
        color=[COLORS["green"]] * 5 + [COLORS["orange"]],
        edgecolor=COLORS["navy"],
        linewidth=0.7,
        capsize=3,
    )
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Mean across seeds")
    ax.set_title("XAI and audit reviewability metrics")
    ax.grid(axis="y", alpha=0.25)
    for bar, value in zip(bars, means, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            min(value + 0.025, 1.04),
            f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    ax.text(
        0.0,
        -0.29,
        "Source: results/tables/explanation_audit_quality_summary.csv. "
        "Text coverage is the known weakness.",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8,
    )
    save(fig, "fig_05_xai_audit_quality.svg")


def figure_workload_stress() -> None:
    stress = pd.read_csv(TABLES / "workload_policy_stress_summary.csv")
    size = stress[stress["arm"] == "size_baseline"].sort_values("num_requests")
    x = size["num_requests"]

    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.plot(x, size["cs_f25_nspi_global_detect"], marker="o", label="25% NS-PI global")
    ax.plot(x, size["cs_f10_nspi_global_detect"], marker="s", label="10% NS-PI global")
    ax.plot(
        x,
        size["cs_f10_nspi_per_station_detect"],
        marker="^",
        label="10% NS-PI per-station",
    )
    ax.set_xscale("log")
    ax.set_xticks(x)
    ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
    ax.set_ylim(-0.05, 1.08)
    ax.set_xlabel("Workload size (requests)")
    ax.set_ylabel("Detection rate")
    ax.set_title("Workload-size effect for compromised-signer stress")
    ax.grid(alpha=0.25)
    ax.legend(loc="lower right")
    ax.text(
        0.0,
        -0.26,
        "Source: results/tables/workload_policy_stress_summary.csv. "
        "Five synthetic seeds per point.",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8,
    )
    save(fig, "fig_06_workload_stress_detection.svg")


def main() -> int:
    setup()
    figure_architecture()
    figure_visibility()
    figure_compromised_signer()
    figure_sensitivity()
    figure_xai_quality()
    figure_workload_stress()
    print(f"Wrote paper figures to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
