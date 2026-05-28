"""Synthetic detector background, signal, and threshold-crossing calculations."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd


def _as_array(values: Any) -> np.ndarray:
    """Return values as a floating array; units are inherited from values."""
    return np.asarray(values, dtype=float)


def simulate_background(
    mean_background: float,
    sigma_background: float,
    n_steps: int,
    seed: int | None = None,
    model: str = "normal",
) -> np.ndarray:
    """Return simulated detector background counts for n_steps integration periods."""
    mean = float(mean_background)
    sigma = float(sigma_background)
    steps = int(n_steps)
    if mean < 0.0:
        raise ValueError("mean_background must be nonnegative.")
    if sigma < 0.0:
        raise ValueError("sigma_background must be nonnegative.")
    if steps <= 0:
        raise ValueError("n_steps must be positive.")
    rng = np.random.default_rng(seed)
    if model == "normal":
        return np.clip(rng.normal(mean, sigma, steps), 0.0, None)
    if model == "poisson":
        return rng.poisson(mean, steps).astype(float)
    raise ValueError("model must be 'normal' or 'poisson'.")


def detector_signal(concentration: Any, response_factor: float, background: Any, noise: Any) -> np.ndarray:
    """Return total detector signal counts from concentration in becquerels per cubic meter."""
    response = float(response_factor)
    if response < 0.0:
        raise ValueError("response_factor must be nonnegative.")
    c = _as_array(concentration)
    if np.any(c < 0.0):
        raise ValueError("concentration must be nonnegative.")
    return c * response + _as_array(background) + _as_array(noise)


def threshold_level(background_mean: float, background_sigma: float, n_sigma: float) -> float:
    """Return threshold level in counts for a background mean and sigma in counts."""
    mean = float(background_mean)
    sigma = float(background_sigma)
    n = float(n_sigma)
    if mean < 0.0:
        raise ValueError("background_mean must be nonnegative.")
    if sigma < 0.0:
        raise ValueError("background_sigma must be nonnegative.")
    if n < 0.0:
        raise ValueError("n_sigma must be nonnegative.")
    return mean + n * sigma


def detect_threshold_crossing(signal: Any, threshold: float) -> np.ndarray:
    """Return boolean threshold-crossing states for signal and threshold in counts."""
    return _as_array(signal) > _as_array(threshold)


def time_to_first_threshold_crossing(time_s: Any, signal: Any, threshold: float) -> float | None:
    """Return first threshold-crossing time in seconds, or None when no crossing occurs."""
    times = _as_array(time_s)
    states = detect_threshold_crossing(signal, threshold)
    if len(times) != len(states):
        raise ValueError("time_s and signal must have the same length.")
    crossing_indexes = np.flatnonzero(states)
    if len(crossing_indexes) == 0:
        return None
    return float(times[int(crossing_indexes[0])])


def false_positive_rate(background_only_signals: Any, threshold: float) -> float:
    """Return the fraction of background-only count values above a count threshold."""
    values = _as_array(background_only_signals)
    if values.size == 0:
        raise ValueError("background_only_signals must not be empty.")
    return float(np.mean(values > float(threshold)))


def _row_value(row: Any, name: str, default: Any = None) -> Any:
    """Return a named value from a pandas row or mapping; units depend on field."""
    if isinstance(row, Mapping):
        return row.get(name, default)
    return getattr(row, name, default)


def evaluate_detector_network_timeseries(
    plume_timeseries_df: pd.DataFrame,
    detector_backgrounds_df: pd.DataFrame,
    candidate_detectors_df: pd.DataFrame,
) -> pd.DataFrame:
    """Return plume-plus-background detector time series with signals in counts."""
    if plume_timeseries_df.empty:
        raise ValueError("plume_timeseries_df must contain at least one row.")
    if detector_backgrounds_df.empty:
        raise ValueError("detector_backgrounds_df must contain at least one row.")
    if candidate_detectors_df.empty:
        raise ValueError("candidate_detectors_df must contain at least one row.")

    detector_cols = ["detector_id", "detector_type", "response_factor", "cost_proxy", "uptime_factor"]
    merged = plume_timeseries_df.merge(candidate_detectors_df[detector_cols], on="detector_id", how="left")
    backgrounds = detector_backgrounds_df.copy()
    merged = merged.merge(
        backgrounds[
            [
                "detector_id",
                "scenario_id",
                "background_mean_counts",
                "background_sigma_counts",
                "integration_time_s",
                "noise_model",
                "seed",
            ]
        ],
        on=["detector_id", "scenario_id"],
        how="left",
    )
    missing_background = merged["background_mean_counts"].isna()
    if missing_background.any():
        fallback = backgrounds.drop_duplicates("detector_id").set_index("detector_id")
        for col in [
            "background_mean_counts",
            "background_sigma_counts",
            "integration_time_s",
            "noise_model",
            "seed",
        ]:
            merged.loc[missing_background, col] = merged.loc[missing_background, "detector_id"].map(fallback[col])

    concentration = merged["concentration_Bq_m3"].astype(float).to_numpy()
    response = merged["response_factor"].astype(float).to_numpy()
    background = merged["background_mean_counts"].astype(float).to_numpy()
    merged["net_signal_counts"] = concentration * response
    merged["noise_counts"] = np.zeros(len(merged), dtype=float)
    merged["total_signal_counts"] = merged["net_signal_counts"].to_numpy() + background
    merged["threshold_3sigma_counts"] = [
        threshold_level(row.background_mean_counts, row.background_sigma_counts, 3.0)
        for row in merged.itertuples(index=False)
    ]
    merged["threshold_5sigma_counts"] = [
        threshold_level(row.background_mean_counts, row.background_sigma_counts, 5.0)
        for row in merged.itertuples(index=False)
    ]
    merged["threshold_crossing_3sigma"] = detect_threshold_crossing(
        merged["total_signal_counts"], merged["threshold_3sigma_counts"]
    )
    merged["threshold_crossing_5sigma"] = detect_threshold_crossing(
        merged["total_signal_counts"], merged["threshold_5sigma_counts"]
    )
    return merged
