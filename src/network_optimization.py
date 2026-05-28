"""Sensor network scoring and deterministic selection helpers."""
from __future__ import annotations

import itertools
import math
from collections.abc import Callable, Mapping
from typing import Any

import pandas as pd


DEFAULT_WEIGHTS = {"w1": 0.45, "w2": 0.25, "w3": 0.15, "w4": 0.15}


def _detector_ids(network_detectors: pd.DataFrame | list[str] | tuple[str, ...]) -> list[str]:
    """Return detector identifiers with no units."""
    if isinstance(network_detectors, pd.DataFrame):
        if "detector_id" not in network_detectors.columns:
            return []
        return [str(v) for v in network_detectors["detector_id"].dropna().tolist()]
    return [str(v) for v in network_detectors]


def _as_weights(weights: Mapping[str, float] | None) -> dict[str, float]:
    """Return dimensionless objective weights."""
    if weights is None:
        return DEFAULT_WEIGHTS.copy()
    return {key: float(weights.get(key, DEFAULT_WEIGHTS[key])) for key in DEFAULT_WEIGHTS}


def _normalization_value(normalization: Mapping[str, Any] | None, name: str, default: float) -> float:
    """Return a positive normalization value in the units implied by name."""
    if normalization is None:
        return default
    value = float(normalization.get(name, default))
    if value <= 0.0:
        raise ValueError(f"{name} must be positive.")
    return value


def wind_sector_coverage(network_detectors: pd.DataFrame, sector_definition: Mapping[str, Any]) -> float:
    """Return the fraction of angular wind sectors covered by detector x/y coordinates in meters."""
    if network_detectors.empty:
        return 0.0
    n_sectors = int(sector_definition.get("n_sectors", 8))
    if n_sectors <= 0:
        raise ValueError("n_sectors must be positive.")
    source_x = float(sector_definition.get("source_x_m", 0.0))
    source_y = float(sector_definition.get("source_y_m", 0.0))
    occupied: set[int] = set()
    for row in network_detectors.itertuples(index=False):
        dx = float(row.x_m) - source_x
        dy = float(row.y_m) - source_y
        if dx == 0.0 and dy == 0.0:
            continue
        angle = (math.degrees(math.atan2(dy, dx)) + 360.0) % 360.0
        occupied.add(int(angle // (360.0 / n_sectors)))
    return len(occupied) / n_sectors


def score_network(
    network_detectors: pd.DataFrame | list[str],
    detector_results: pd.DataFrame,
    weights: Mapping[str, float] | None,
    normalization: Mapping[str, Any] | None,
) -> dict[str, float]:
    """Return dimensionless network metrics using time in seconds and cost proxy units."""
    ids = _detector_ids(network_detectors)
    weight = _as_weights(weights)
    t_max = _normalization_value(normalization, "T_max_s", 1200.0)
    c_max = _normalization_value(normalization, "C_max", 5.0)
    selected_results = detector_results[detector_results["detector_id"].astype(str).isin(ids)].copy()
    if "n_sigma" in selected_results.columns:
        selected_results = selected_results[selected_results["n_sigma"].astype(float) == 3.0]

    if ids and not selected_results.empty:
        scenario_count = max(1, detector_results.get("scenario_id", pd.Series(["S1"])).nunique())
        detected_by_scenario = selected_results.dropna(subset=["first_threshold_crossing_s"]).groupby("scenario_id").size()
        p_detect = min(1.0, len(detected_by_scenario) / scenario_count)
        finite_times = pd.to_numeric(selected_results["first_threshold_crossing_s"], errors="coerce").dropna()
        t_detect = float(finite_times.min()) if not finite_times.empty else t_max
    else:
        p_detect = 0.0
        t_detect = t_max

    if isinstance(network_detectors, pd.DataFrame) and not network_detectors.empty:
        cost = float(pd.to_numeric(network_detectors.get("cost_proxy", 0.0), errors="coerce").fillna(0.0).sum())
        coverage = wind_sector_coverage(network_detectors, (normalization or {}).get("sector_definition", {}))
        detector_count = float(len(network_detectors))
    else:
        cost = 0.0
        coverage = 0.0
        detector_count = 0.0

    time_component = 1.0 - min(t_detect, t_max) / t_max
    cost_component = 1.0 - min(cost, c_max) / c_max
    score = (
        weight["w1"] * p_detect
        + weight["w2"] * time_component
        + weight["w3"] * cost_component
        + weight["w4"] * coverage
    )
    return {
        "score": float(score),
        "P_detect": float(p_detect),
        "T_detect_s": float(t_detect),
        "C_cost": float(cost),
        "W_coverage": float(coverage),
        "detector_count": detector_count,
    }


def brute_force_network_search(
    candidate_detectors: pd.DataFrame,
    k: int,
    objective_function: Callable[[pd.DataFrame], Mapping[str, float] | float],
) -> pd.DataFrame:
    """Return brute-force network scores for k detector combinations; scores are dimensionless."""
    if k < 0:
        raise ValueError("k must be nonnegative.")
    if k > len(candidate_detectors):
        raise ValueError("k cannot exceed number of candidate detectors.")
    rows: list[dict[str, Any]] = []
    for combo in itertools.combinations(candidate_detectors["detector_id"].tolist(), k):
        subset = candidate_detectors[candidate_detectors["detector_id"].isin(combo)].copy()
        result = objective_function(subset)
        if isinstance(result, Mapping):
            score = float(result.get("score", 0.0))
            metrics = dict(result)
        else:
            score = float(result)
            metrics = {"score": score}
        rows.append({"detector_ids": ";".join(combo), **metrics, "score": score})
    return pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)


def greedy_network_selection(
    candidate_detectors: pd.DataFrame,
    k_max: int,
    objective_function: Callable[[pd.DataFrame], Mapping[str, float] | float],
) -> pd.DataFrame:
    """Return greedy detector selection history with dimensionless scores."""
    if k_max < 0:
        raise ValueError("k_max must be nonnegative.")
    selected: list[str] = []
    remaining = [str(v) for v in candidate_detectors["detector_id"].tolist()]
    rows: list[dict[str, Any]] = []
    for step in range(1, min(k_max, len(remaining)) + 1):
        best_id: str | None = None
        best_metrics: dict[str, float] | None = None
        best_score = -float("inf")
        for detector_id in remaining:
            trial_ids = selected + [detector_id]
            subset = candidate_detectors[candidate_detectors["detector_id"].isin(trial_ids)].copy()
            result = objective_function(subset)
            metrics = dict(result) if isinstance(result, Mapping) else {"score": float(result)}
            score = float(metrics.get("score", 0.0))
            if score > best_score or (score == best_score and (best_id is None or detector_id < best_id)):
                best_id = detector_id
                best_metrics = metrics
                best_score = score
        if best_id is None or best_metrics is None:
            break
        selected.append(best_id)
        remaining.remove(best_id)
        rows.append(
            {
                "step": step,
                "added_detector_id": best_id,
                "selected_detector_ids": ";".join(selected),
                **best_metrics,
            }
        )
    return pd.DataFrame(rows)


def compare_network_designs(network_definitions: pd.DataFrame, detector_results: pd.DataFrame) -> pd.DataFrame:
    """Return comparison metrics for named networks with time in seconds and dimensionless scores."""
    if "network_id" not in network_definitions.columns:
        raise ValueError("network_definitions must include network_id.")
    normalization = {
        "T_max_s": 1200.0,
        "C_max": max(1.0, float(network_definitions.get("cost_proxy", pd.Series([0.0])).sum())),
        "sector_definition": {"n_sectors": 8, "source_x_m": 0.0, "source_y_m": 0.0},
    }
    rows: list[dict[str, Any]] = []
    for network_id, group in network_definitions.groupby("network_id", sort=True):
        group = group.dropna(subset=["detector_id"]) if "detector_id" in group else group
        metrics = score_network(group, detector_results, DEFAULT_WEIGHTS, normalization)
        rows.append({"network_id": network_id, **metrics})
    return pd.DataFrame(rows)
