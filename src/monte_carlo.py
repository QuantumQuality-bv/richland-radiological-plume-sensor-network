"""Monte Carlo uncertainty propagation for the synthetic pipeline."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .detector_model import threshold_level
from .plume_gaussian import gaussian_plume_concentration, sigma_y, sigma_z


def _config_value(config: dict[str, Any], name: str, default: float) -> float:
    """Return a scalar configuration value with units encoded in its key."""
    return float(config.get(name, default))


def sample_uncertain_inputs(config: dict[str, Any], n_samples: int, seed: int | None = None) -> pd.DataFrame:
    """Return Monte Carlo samples with physical units encoded in column names."""
    n = int(n_samples)
    if n <= 0:
        raise ValueError("n_samples must be positive.")
    rng = np.random.default_rng(seed)
    base_wind = _config_value(config, "wind_speed_mps", 3.0)
    source_multiplier = rng.lognormal(mean=0.0, sigma=0.45, size=n)
    wind_speed = np.clip(rng.normal(base_wind, 0.25 * base_wind, size=n), 0.2, None)
    wind_dir = rng.normal(_config_value(config, "wind_dir_deg", 0.0), 10.0, size=n)
    background_mean = np.clip(rng.normal(_config_value(config, "background_mean_counts", 7200.0), 120.0, size=n), 0.0, None)
    response_error = rng.normal(1.0, 0.10, size=n)
    sigma_y_multiplier = rng.lognormal(mean=0.0, sigma=0.25, size=n)
    sigma_z_multiplier = rng.lognormal(mean=0.0, sigma=0.25, size=n)
    rows = pd.DataFrame(
        {
            "sample_id": np.arange(1, n + 1),
            "source_multiplier": source_multiplier,
            "wind_speed_mps": wind_speed,
            "wind_dir_deg": wind_dir,
            "background_mean_counts": background_mean,
            "response_error": response_error,
            "sigma_y_multiplier": sigma_y_multiplier,
            "sigma_z_multiplier": sigma_z_multiplier,
            "Q_dot_Bq_s": _config_value(config, "Q_dot_Bq_s", 8.333333333333334),
            "response_factor": _config_value(config, "response_factor", 1.0e6),
            "background_sigma_counts": _config_value(config, "background_sigma_counts", 84.85),
            "threshold_n_sigma": _config_value(config, "threshold_n_sigma", 3.0),
            "x_m": _config_value(config, "x_m", 1000.0),
            "y_m": _config_value(config, "y_m", 0.0),
        }
    )
    return rows


def run_single_monte_carlo_sample(sample_row: pd.Series | dict[str, Any]) -> dict[str, Any]:
    """Return one Monte Carlo result with concentration in becquerels per cubic meter."""
    row = sample_row if isinstance(sample_row, dict) else sample_row.to_dict()
    x = float(row["x_m"])
    y = float(row["y_m"])
    sy = sigma_y(x) * float(row["sigma_y_multiplier"])
    sz = sigma_z(x) * float(row["sigma_z_multiplier"])
    q = float(row["Q_dot_Bq_s"]) * float(row["source_multiplier"])
    concentration = gaussian_plume_concentration(q, float(row["wind_speed_mps"]), sy, sz, y, 0.0, 0.0)
    response_factor = float(row["response_factor"]) * max(0.0, float(row["response_error"]))
    net_signal = concentration * response_factor
    total_signal = float(row["background_mean_counts"]) + net_signal
    threshold = threshold_level(row["background_mean_counts"], row["background_sigma_counts"], row["threshold_n_sigma"])
    detected = bool(total_signal > threshold)
    time_to_detection = x / float(row["wind_speed_mps"]) if detected else np.nan
    localization_error = abs(float(row["wind_dir_deg"])) * 5.0 + abs(float(row["sigma_y_multiplier"]) - 1.0) * 50.0
    return {
        "sample_id": int(row["sample_id"]),
        "concentration_Bq_m3": concentration,
        "net_signal_counts": net_signal,
        "total_signal_counts": total_signal,
        "threshold_counts": threshold,
        "detected": detected,
        "time_to_detection_s": time_to_detection,
        "localization_error_m": localization_error,
    }


def run_monte_carlo(samples_df: pd.DataFrame) -> pd.DataFrame:
    """Return Monte Carlo results with time in seconds and error in meters."""
    if samples_df.empty:
        raise ValueError("samples_df must not be empty.")
    return pd.DataFrame([run_single_monte_carlo_sample(row) for _, row in samples_df.iterrows()])


def compute_percentile_summary(results_df: pd.DataFrame, percentiles: list[int] | None = None) -> pd.DataFrame:
    """Return percentile summary for numeric Monte Carlo outputs; percentiles are dimensionless."""
    if percentiles is None:
        percentiles = [5, 50, 95]
    if results_df.empty:
        raise ValueError("results_df must not be empty.")
    variables = [
        "concentration_Bq_m3",
        "net_signal_counts",
        "total_signal_counts",
        "time_to_detection_s",
        "localization_error_m",
    ]
    rows: list[dict[str, float | str]] = []
    for variable in variables:
        values = pd.to_numeric(results_df[variable], errors="coerce").dropna().to_numpy()
        if values.size == 0:
            continue
        for percentile in percentiles:
            rows.append({"variable": variable, "percentile": float(percentile), "value": float(np.percentile(values, percentile))})
    return pd.DataFrame(rows)


def estimate_detection_probability(results_df: pd.DataFrame) -> float:
    """Return the Monte Carlo threshold-crossing probability as a dimensionless fraction."""
    if results_df.empty:
        raise ValueError("results_df must not be empty.")
    return float(results_df["detected"].astype(bool).mean())


def export_monte_carlo_outputs(results_df: pd.DataFrame, summary_df: pd.DataFrame) -> None:
    """Write Monte Carlo results and percentile summary CSV files to data/processed."""
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "data" / "processed" / "monte_carlo_outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(out_dir / "monte_carlo_results.csv", index=False)
    summary_df.to_csv(out_dir / "monte_carlo_percentiles.csv", index=False)
