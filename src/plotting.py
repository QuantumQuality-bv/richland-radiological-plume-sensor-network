"""Final figure generation helpers for synthetic modeling outputs."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LogNorm

plt.ioff()

FINAL_FIGURES = [
    {
        "figure_id": "plume_log_contour",
        "inputs": "data/processed/plume_outputs/plume_grid.csv; data/synthetic/synthetic_receptors.csv",
        "purpose": "Log-scaled Gaussian plume concentration field with validation receptors.",
        "section": "Synthetic source and plume model",
        "status": "final/main",
    },
    {
        "figure_id": "centerline_profile",
        "inputs": "data/processed/plume_outputs/centerline_profile.csv",
        "purpose": "Downwind centerline concentration profile.",
        "section": "Synthetic source and plume model",
        "status": "final/main",
    },
    {
        "figure_id": "crosswind_profile",
        "inputs": "data/processed/plume_outputs/crosswind_profile.csv",
        "purpose": "Crosswind concentration profile at the baseline downwind distance.",
        "section": "Synthetic source and plume model",
        "status": "final/main",
    },
    {
        "figure_id": "detector_timeseries",
        "inputs": "data/processed/detector_outputs/detector_timeseries.csv; data/processed/detector_outputs/time_to_threshold.csv",
        "purpose": "Detector count time series with synthetic threshold crossings.",
        "section": "Detector response simulation",
        "status": "final/main",
    },
    {
        "figure_id": "network_metrics",
        "inputs": "data/processed/network_outputs/network_metrics.csv",
        "purpose": "Comparison of score, probability, cost proxy, and wind-sector coverage.",
        "section": "Sensor network comparison",
        "status": "final/main",
    },
    {
        "figure_id": "detection_probability_by_network",
        "inputs": "data/processed/network_outputs/network_metrics.csv",
        "purpose": "Detection probability by candidate network.",
        "section": "Sensor network comparison",
        "status": "optional/supporting",
    },
    {
        "figure_id": "src_recon_likelihood",
        "inputs": "data/processed/source_reconstruction_outputs/noisy_likelihood_grid.csv",
        "purpose": "Noisy synthetic source reconstruction objective surface.",
        "section": "Source reconstruction and uncertainty",
        "status": "final/main",
    },
    {
        "figure_id": "src_recon_error_dist",
        "inputs": "data/processed/monte_carlo_outputs/loc_error_dist.csv",
        "purpose": "Monte Carlo localization error distribution.",
        "section": "Source reconstruction and uncertainty",
        "status": "final/main",
    },
    {
        "figure_id": "sensitivity_tornado",
        "inputs": "data/processed/sensitivity_outputs/sensitivity_tornado.csv",
        "purpose": "One-at-a-time concentration sensitivity tornado chart.",
        "section": "Sensitivity and Monte Carlo",
        "status": "final/main",
    },
    {
        "figure_id": "mc_conc_dist",
        "inputs": "data/processed/monte_carlo_outputs/monte_carlo_results_final.csv",
        "purpose": "Final Monte Carlo concentration distribution.",
        "section": "Sensitivity and Monte Carlo",
        "status": "optional/supporting",
    },
    {
        "figure_id": "mc_ttd_dist",
        "inputs": "data/processed/monte_carlo_outputs/monte_carlo_results_final.csv",
        "purpose": "Final Monte Carlo time-to-threshold distribution.",
        "section": "Sensitivity and Monte Carlo",
        "status": "optional/supporting",
    },
    {
        "figure_id": "mc_loc_error_dist",
        "inputs": "data/processed/monte_carlo_outputs/monte_carlo_results_final.csv",
        "purpose": "Final Monte Carlo localization error distribution.",
        "section": "Sensitivity and Monte Carlo",
        "status": "optional/supporting",
    },
    {
        "figure_id": "mc_uncertainty_summary",
        "inputs": "data/processed/monte_carlo_outputs/monte_carlo_results_final.csv",
        "purpose": "Three-panel Monte Carlo uncertainty summary.",
        "section": "Sensitivity and Monte Carlo",
        "status": "final/main",
    },
]


def _read_csv(root: Path, rel_path: str) -> pd.DataFrame:
    path = root / rel_path
    if not path.exists():
        raise FileNotFoundError(f"Missing required plotting input: {rel_path}")
    return pd.read_csv(path)


def _concentration_column(df: pd.DataFrame) -> str:
    for name in ("concentration_bq_m3", "concentration_Bq_m3", "concentration_Bq_m3"):
        if name in df.columns:
            return name
    raise KeyError("No concentration column found.")


def _save(fig: plt.Figure, root: Path, basename: str) -> list[dict[str, str]]:
    rows = []
    out_dir = root / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        path = out_dir / f"{basename}.{ext}"
        fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
        rows.append({"figure_id": basename, "file": f"figures/{basename}.{ext}"})
    plt.close(fig)
    plt.close("all")
    return rows


def _style_axes(ax: plt.Axes) -> None:
    ax.tick_params(colors="#222222", labelsize=9)
    for spine in ax.spines.values():
        spine.set_color("#333333")


def _percentile_lines(ax: plt.Axes, values: pd.Series, unit_label: str) -> None:
    clean = pd.to_numeric(values, errors="coerce").dropna()
    if clean.empty:
        ax.text(0.5, 0.5, "No finite samples", transform=ax.transAxes, ha="center", va="center")
        return
    for pct, color in [(5, "#6f6f6f"), (50, "#111111"), (95, "#6f6f6f")]:
        value = float(np.percentile(clean, pct))
        ax.axvline(value, color=color, linewidth=1.2, linestyle="-" if pct == 50 else "--", label=f"{pct}th")
    ax.set_xlabel(unit_label)


def plume_contour(root: Path) -> list[dict[str, str]]:
    grid = _read_csv(root, "data/processed/plume_outputs/plume_grid.csv")
    receptors = _read_csv(root, "data/synthetic/synthetic_receptors.csv")
    c_col = _concentration_column(grid)
    view = grid[(grid["x_m"].between(0.0, 2500.0)) & (grid["y_m"].between(-500.0, 500.0))].copy()
    positive = view[pd.to_numeric(view[c_col], errors="coerce") > 0.0]
    if positive.empty:
        raise ValueError("Plume grid has no positive concentrations in the plotting view.")

    c = positive[c_col].to_numpy(dtype=float)
    vmin = max(float(np.nanpercentile(c, 2)), float(np.nanmax(c)) * 1.0e-5)
    vmax = float(np.nanmax(c))
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    contour = ax.tricontourf(
        positive["x_m"],
        positive["y_m"],
        c,
        levels=np.geomspace(vmin, vmax, 24),
        norm=LogNorm(vmin=vmin, vmax=vmax),
        cmap="viridis",
    )
    for collection in getattr(contour, "collections", []):
        collection.set_rasterized(True)
    cbar = fig.colorbar(contour, ax=ax, pad=0.02)
    cbar.set_label("Air concentration proxy, C (Bq m$^{-3}$)", fontsize=10)
    cbar.ax.tick_params(labelsize=8)
    ax.scatter([0.0], [0.0], marker="*", s=130, color="#d62728", edgecolor="black", linewidth=0.5, label="Synthetic source")

    key_receptors = {"R001", "R002", "R003", "R004", "R005", "R010"}
    rec = receptors[receptors["receptor_id"].isin(key_receptors)]
    rec = rec[rec["x_m"].between(0.0, 2500.0) & rec["y_m"].between(-500.0, 500.0)]
    ax.scatter(rec["x_m"], rec["y_m"], marker="o", s=34, color="white", edgecolor="black", linewidth=0.8, label="Validation receptor")
    for row in rec.itertuples(index=False):
        ax.annotate(row.receptor_id, (row.x_m, row.y_m), xytext=(5, 5), textcoords="offset points", fontsize=8)
    ax.annotate("wind direction", xy=(650, 420), xytext=(150, 420), arrowprops={"arrowstyle": "->", "lw": 1.5}, fontsize=9)
    ax.set_xlim(0.0, 2500.0)
    ax.set_ylim(-500.0, 500.0)
    ax.set_xlabel("Downwind distance x (m)")
    ax.set_ylabel("Crosswind distance y (m)")
    ax.set_title("Synthetic Gaussian Plume, Log-Scaled Concentration", fontsize=12)
    ax.legend(loc="upper right", fontsize=8, frameon=True)
    _style_axes(ax)
    return _save(fig, root, "plume_log_contour")


def centerline_profile(root: Path) -> list[dict[str, str]]:
    df = _read_csv(root, "data/processed/plume_outputs/centerline_profile.csv")
    c_col = _concentration_column(df)
    x_col = "x_downwind_m" if "x_downwind_m" in df.columns else "x_m"
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.plot(df[x_col], df[c_col], color="#1f77b4", linewidth=2.0)
    for x in (500.0, 1000.0, 2000.0):
        ax.axvline(x, color="#777777", linewidth=0.9, linestyle="--")
    ax.set_yscale("log")
    ax.set_xlabel("Downwind distance x (m)")
    ax.set_ylabel("C (Bq m$^{-3}$)")
    ax.set_title("Centerline Concentration Profile", fontsize=12)
    _style_axes(ax)
    return _save(fig, root, "centerline_profile")


def crosswind_profile(root: Path) -> list[dict[str, str]]:
    df = _read_csv(root, "data/processed/plume_outputs/crosswind_profile.csv")
    c_col = _concentration_column(df)
    y_col = "y_crosswind_m" if "y_crosswind_m" in df.columns else "y_m"
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.plot(df[y_col], df[c_col], color="#2ca02c", linewidth=2.0)
    ax.axvline(0.0, color="#111111", linewidth=1.0, linestyle="--", label="Centerline")
    ax.axvline(200.0, color="#777777", linewidth=1.0, linestyle=":", label="R002 offset")
    ax.set_xlabel("Crosswind distance y (m)")
    ax.set_ylabel("C (Bq m$^{-3}$)")
    ax.set_title("Crosswind Concentration Profile at x = 1000 m", fontsize=12)
    ax.legend(fontsize=8)
    _style_axes(ax)
    return _save(fig, root, "crosswind_profile")


def detector_timeseries(root: Path) -> list[dict[str, str]]:
    df = _read_csv(root, "data/processed/detector_outputs/detector_timeseries.csv")
    thresholds = _read_csv(root, "data/processed/detector_outputs/time_to_threshold.csv")
    detector_ids = [d for d in ["D001", "D002", "D003", "D004"] if d in set(df["detector_id"])]
    fig, axes = plt.subplots(len(detector_ids), 1, figsize=(7.2, 6.4), sharex=True)
    if len(detector_ids) == 1:
        axes = [axes]
    for ax, detector_id in zip(axes, detector_ids):
        g = df[df["detector_id"] == detector_id].sort_values("time_s")
        t_min = g["time_s"] / 60.0
        ax.plot(t_min, g["total_signal_counts"], color="#1f77b4", linewidth=1.6, label="Total signal")
        ax.plot(t_min, g["background_mean_counts"], color="#4d4d4d", linewidth=1.1, linestyle="--", label="Background mean")
        ax.plot(t_min, g["threshold_3sigma_counts"], color="#ff7f0e", linewidth=1.1, label="3-sigma threshold")
        ax.plot(t_min, g["threshold_5sigma_counts"], color="#d62728", linewidth=1.1, label="5-sigma threshold")
        for n_sigma, color in [(3.0, "#ff7f0e"), (5.0, "#d62728")]:
            rows = thresholds[(thresholds["detector_id"] == detector_id) & (thresholds["n_sigma"] == n_sigma)]
            if not rows.empty and pd.notna(rows.iloc[0]["first_threshold_crossing_s"]):
                t_cross = float(rows.iloc[0]["first_threshold_crossing_s"]) / 60.0
                ax.axvline(t_cross, color=color, linewidth=0.9, linestyle=":")
                if detector_id in {"D001", "D002"}:
                    ax.annotate(f"{int(n_sigma)}-sigma", (t_cross, ax.get_ylim()[1]), xytext=(3, -13), textcoords="offset points", fontsize=8)
        ax.set_ylabel(f"{detector_id}\ncounts")
        _style_axes(ax)
    axes[0].legend(loc="upper right", fontsize=8, ncol=2)
    axes[-1].set_xlabel("Time (min)")
    fig.suptitle("Detector Time Series and Synthetic Threshold Crossings", fontsize=12)
    fig.tight_layout()
    return _save(fig, root, "detector_timeseries")


def network_metrics(root: Path, include_optional: bool = False) -> list[dict[str, str]]:
    df = _read_csv(root, "data/processed/network_outputs/network_metrics.csv").sort_values("network_id")
    metrics = pd.DataFrame(
        {
            "network_id": df["network_id"],
            "Score": df["score"],
            "P_detect": df["P_detect"],
            "Cost proxy (normalized)": df["C_cost"] / max(float(df["C_cost"].max()), 1.0),
            "Wind-sector coverage": df["W_coverage"],
        }
    )
    x = np.arange(len(metrics))
    width = 0.18
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    for idx, col in enumerate(metrics.columns[1:]):
        ax.bar(x + (idx - 1.5) * width, metrics[col], width=width, label=col)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics["network_id"])
    ax.set_ylim(0.0, 1.15)
    ax.set_ylabel("Normalized metric value")
    ax.set_title("Network Metric Comparison", fontsize=12)
    ax.legend(fontsize=8, ncol=2)
    _style_axes(ax)
    rows = _save(fig, root, "network_metrics")

    if include_optional:
        fig2, ax2 = plt.subplots(figsize=(5.8, 3.6))
        bars = ax2.bar(df["network_id"], df["P_detect"], color="#1f77b4")
        for bar in bars:
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02, f"{bar.get_height():.2f}", ha="center", fontsize=8)
        ax2.set_ylim(0.0, 1.15)
        ax2.set_xlabel("Network")
        ax2.set_ylabel("P_detect")
        ax2.set_title("Detection Probability by Network", fontsize=12)
        _style_axes(ax2)
        rows.extend(_save(fig2, root, "detection_probability_by_network"))
    return rows


def source_reconstruction(root: Path) -> list[dict[str, str]]:
    out_dir = root / "data" / "processed" / "source_reconstruction_outputs"
    likelihood_path = out_dir / "noisy_likelihood_grid.csv"
    estimate_path = out_dir / "noisy_source_estimate.csv"
    error_path = out_dir / "noisy_loc_error_summary.csv"
    if not likelihood_path.exists():
        likelihood_path = out_dir / "likelihood_grid.csv"
        estimate_path = out_dir / "source_estimate.csv"
        error_path = out_dir / "localization_error_summary.csv"
    likelihood = pd.read_csv(likelihood_path)
    estimate = pd.read_csv(estimate_path).iloc[0]
    error_summary = pd.read_csv(error_path).iloc[0]
    detectors = _read_csv(root, "data/synthetic/candidate_detectors.csv")
    selected = detectors[detectors["detector_id"].isin(["D001", "D002", "D003", "D004", "D005"])]

    delta_j = likelihood["J"] - float(likelihood["J"].min())
    vmax = max(float(np.nanpercentile(delta_j, 95)), 1.0)
    fig, ax = plt.subplots(figsize=(5.8, 5.0))
    contour = ax.tricontourf(likelihood["x_m"], likelihood["y_m"], delta_j, levels=np.linspace(0.0, vmax, 18), cmap="magma_r")
    for collection in getattr(contour, "collections", []):
        collection.set_rasterized(True)
    ax.tricontour(likelihood["x_m"], likelihood["y_m"], delta_j, levels=np.linspace(0.0, vmax, 8), colors="black", linewidths=0.35, alpha=0.45)
    cbar = fig.colorbar(contour, ax=ax, pad=0.02)
    cbar.set_label("Delta J = J - J_min", fontsize=10)
    ax.scatter(selected["x_m"], selected["y_m"], marker="^", s=45, color="white", edgecolor="black", label="Selected detector")
    ax.scatter([error_summary["true_x_m"]], [error_summary["true_y_m"]], marker="*", s=140, color="#2ca02c", edgecolor="black", label="True source")
    ax.scatter([estimate["estimated_x_m"]], [estimate["estimated_y_m"]], marker="X", s=95, color="#d62728", edgecolor="black", label="Estimated source")
    ax.text(0.02, 0.02, f"Localization error: {float(error_summary['localization_error_m']):.1f} m", transform=ax.transAxes, fontsize=9, bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "#cccccc"})
    ax.set_xlabel("Candidate x (m)")
    ax.set_ylabel("Candidate y (m)")
    ax.set_title("Noisy Synthetic Source Reconstruction Surface", fontsize=12)
    ax.legend(loc="upper right", fontsize=8)
    ax.set_aspect("equal", adjustable="box")
    _style_axes(ax)
    rows = _save(fig, root, "src_recon_likelihood")

    errors = _read_csv(root, "data/processed/monte_carlo_outputs/loc_error_dist.csv")
    fig2, ax2 = plt.subplots(figsize=(5.8, 3.6))
    vals = pd.to_numeric(errors["localization_error_m"], errors="coerce").dropna()
    ax2.hist(vals, bins=30, color="#9467bd", edgecolor="white")
    _percentile_lines(ax2, vals, "Localization error (m)")
    ax2.set_ylabel("Sample count")
    ax2.set_title("Monte Carlo Localization Error Distribution", fontsize=12)
    ax2.legend(fontsize=8)
    _style_axes(ax2)
    rows.extend(_save(fig2, root, "src_recon_error_dist"))
    return rows


def sensitivity_tornado(root: Path) -> list[dict[str, str]]:
    df = _read_csv(root, "data/processed/sensitivity_outputs/sensitivity_tornado.csv").copy()
    label_map = {
        "ARF": "ARF",
        "RF": "RF",
        "LPF": "LPF",
        "wind_speed_mps": "Wind speed",
        "duration_s": "Duration",
        "sigma_y_multiplier": "sigma_y",
        "sigma_z_multiplier": "sigma_z",
        "source_multiplier": "Source multiplier",
    }
    if "parameter" in df.columns and "factor" in df.columns:
        labels = []
        for row in df.itertuples(index=False):
            parameter = label_map.get(str(row.parameter), str(row.parameter))
            factor = float(row.factor)
            if str(row.parameter) == "sigma_y_multiplier":
                labels.append(r"$\sigma_y \times$ " + f"{factor:.3g}")
            elif str(row.parameter) == "sigma_z_multiplier":
                labels.append(r"$\sigma_z \times$ " + f"{factor:.3g}")
            elif str(row.parameter) == "threshold_n_sigma":
                labels.append(r"Threshold n $\times$ " + f"{factor:.3g}")
            else:
                labels.append(f"{parameter} " + r"$\times$ " + f"{factor:.3g}")
        df["display_label"] = labels
    else:
        df["display_label"] = df["case_id"].astype(str)
    df = df.sort_values("concentration_pct_change", key=lambda s: s.abs(), ascending=True)
    fig, ax = plt.subplots(figsize=(6.8, 4.8))
    colors = np.where(df["concentration_pct_change"] >= 0.0, "#1f77b4", "#d62728")
    ax.barh(df["display_label"], df["concentration_pct_change"], color=colors)
    ax.axvline(0.0, color="#111111", linewidth=1.0)
    ax.set_xlabel("Concentration change (%)")
    ax.set_title("One-at-a-Time Sensitivity Tornado", fontsize=12)
    _style_axes(ax)
    return _save(fig, root, "sensitivity_tornado")


def monte_carlo_distributions(root: Path, include_optional: bool = False) -> list[dict[str, str]]:
    path = root / "data" / "processed" / "monte_carlo_outputs" / "monte_carlo_results_final.csv"
    if not path.exists():
        path = root / "data" / "processed" / "monte_carlo_outputs" / "monte_carlo_results.csv"
    df = pd.read_csv(path)
    n_label = f"N = {len(df)}"
    specs = [
        ("mc_conc_dist", "concentration_Bq_m3", "C (Bq m$^{-3}$)", "Monte Carlo Concentration Distribution"),
        ("mc_ttd_dist", "time_to_detection_s", "Time to threshold crossing (s)", "Monte Carlo Time-to-Threshold Distribution"),
        ("mc_loc_error_dist", "localization_error_m", "Localization error (m)", "Monte Carlo Localization Error Distribution"),
    ]
    rows: list[dict[str, str]] = []
    if include_optional:
        for basename, col, xlabel, title in specs:
            fig, ax = plt.subplots(figsize=(5.8, 3.6))
            vals = pd.to_numeric(df[col], errors="coerce").dropna()
            ax.hist(vals, bins=35, color="#1f77b4", edgecolor="white")
            _percentile_lines(ax, vals, xlabel)
            ax.set_ylabel("Sample count")
            ax.set_title(f"{title} ({n_label})", fontsize=12)
            ax.legend(fontsize=8)
            _style_axes(ax)
            rows.extend(_save(fig, root, basename))

    fig, axes = plt.subplots(1, 3, figsize=(10.0, 3.2))
    for ax, (_, col, xlabel, title) in zip(axes, specs):
        vals = pd.to_numeric(df[col], errors="coerce").dropna()
        ax.hist(vals, bins=30, color="#4c78a8", edgecolor="white")
        _percentile_lines(ax, vals, xlabel)
        ax.set_title(title.replace("Monte Carlo ", ""), fontsize=10)
        ax.set_ylabel("Count")
        _style_axes(ax)
    axes[-1].legend(fontsize=7)
    fig.suptitle(f"Monte Carlo Uncertainty Summary ({n_label})", fontsize=12)
    fig.tight_layout()
    rows.extend(_save(fig, root, "mc_uncertainty_summary"))
    return rows


def generate_all_figures(root: Path, include_optional: bool = False) -> pd.DataFrame:
    """Generate all final figures and return file manifest rows."""
    root = Path(root)
    rows: list[dict[str, str]] = []
    all_makers = (
        ("plume_contour", plume_contour, False),
        ("centerline_profile", centerline_profile, False),
        ("crosswind_profile", crosswind_profile, False),
        ("detector_timeseries", detector_timeseries, False),
        ("network_metrics", network_metrics, True),
        ("src_recon_likelihood", source_reconstruction, False),
        ("sensitivity_tornado", sensitivity_tornado, False),
        ("mc_uncertainty_summary", monte_carlo_distributions, True),
    )
    for label, maker, supports_optional in all_makers:
        print(f"Generating {label}...", flush=True)
        if supports_optional:
            generated = maker(root, include_optional=include_optional)
        else:
            generated = maker(root)
        rows.extend(generated)
        print(f"Finished {label}", flush=True)
        plt.close("all")

    spec_by_id = {item["figure_id"]: item for item in FINAL_FIGURES}
    manifest_rows = []
    for row in rows:
        spec = spec_by_id.get(row["figure_id"], {})
        manifest_rows.append(
            {
                "figure_id": row["figure_id"],
                "file": row["file"],
                "generating_script": "scripts/10_generate_figures.py",
                "input_csvs": spec.get("inputs", ""),
                "purpose": spec.get("purpose", ""),
                "report_section": spec.get("section", ""),
                "status": spec.get("status", "final/main"),
            }
        )
    return pd.DataFrame(manifest_rows)
