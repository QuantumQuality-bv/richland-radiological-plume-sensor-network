"""One-at-a-time sensitivity calculations for the synthetic modeling pipeline."""
from __future__ import annotations

import copy
from typing import Any

import pandas as pd

from .detector_model import threshold_level
from .plume_gaussian import gaussian_plume_concentration, sigma_y, sigma_z
from .source_term import radiological_source_term, release_rate


def _nominal_defaults() -> dict[str, float]:
    """Return nominal configuration values with units encoded in keys."""
    return {
        "MAR_Bq": 1.0e9,
        "DR": 0.10,
        "ARF": 1.0e-3,
        "RF": 0.50,
        "LPF": 0.10,
        "duration_s": 600.0,
        "wind_speed_mps": 3.0,
        "x_m": 1000.0,
        "y_m": 0.0,
        "z_m": 0.0,
        "H_m": 0.0,
        "sigma_y_multiplier": 1.0,
        "sigma_z_multiplier": 1.0,
        "background_mean_counts": 7200.0,
        "background_sigma_counts": 84.85,
        "response_factor": 1.0e6,
        "threshold_n_sigma": 3.0,
    }


def one_at_a_time_parameter_sets(nominal_config: dict[str, Any]) -> list[dict[str, Any]]:
    """Return one-at-a-time parameter sets with physical units encoded in keys."""
    base = {**_nominal_defaults(), **nominal_config}
    variations = [
        ("ARF", 0.1, "ARF_x0p1"),
        ("ARF", 10.0, "ARF_x10"),
        ("LPF", 0.1, "LPF_x0p1"),
        ("LPF", 10.0, "LPF_x10"),
        ("wind_speed_mps", 0.5, "wind_speed_x0p5"),
        ("wind_speed_mps", 2.0, "wind_speed_x2"),
        ("duration_s", 0.5, "duration_x0p5"),
        ("duration_s", 2.0, "duration_x2"),
        ("sigma_y_multiplier", 0.5, "sigma_y_x0p5"),
        ("sigma_y_multiplier", 2.0, "sigma_y_x2"),
        ("sigma_z_multiplier", 0.5, "sigma_z_x0p5"),
        ("sigma_z_multiplier", 2.0, "sigma_z_x2"),
    ]
    sets: list[dict[str, Any]] = []
    for parameter, factor, case_id in variations:
        config = copy.deepcopy(base)
        config[parameter] = float(config[parameter]) * factor
        if parameter in {"ARF", "LPF"}:
            config[parameter] = min(1.0, max(0.0, config[parameter]))
        sets.append({"case_id": case_id, "parameter": parameter, "factor": factor, "config": config})

    threshold_config = copy.deepcopy(base)
    threshold_config["threshold_n_sigma"] = 5.0
    sets.append({"case_id": "threshold_5sigma", "parameter": "threshold_n_sigma", "factor": 5.0 / 3.0, "config": threshold_config})
    return sets


def run_sensitivity_case(parameter_set: dict[str, Any]) -> dict[str, Any]:
    """Return case metrics with concentration in becquerels per cubic meter and signal in counts."""
    config = {**_nominal_defaults(), **parameter_set.get("config", parameter_set)}
    q_total = radiological_source_term(config["MAR_Bq"], config["DR"], config["ARF"], config["RF"], config["LPF"])
    q_dot = release_rate(q_total, config["duration_s"])
    sy = sigma_y(config["x_m"]) * float(config["sigma_y_multiplier"])
    sz = sigma_z(config["x_m"]) * float(config["sigma_z_multiplier"])
    concentration = gaussian_plume_concentration(
        q_dot,
        config["wind_speed_mps"],
        sy,
        sz,
        config["y_m"],
        config["z_m"],
        config["H_m"],
    )
    net_signal = concentration * float(config["response_factor"])
    threshold = threshold_level(config["background_mean_counts"], config["background_sigma_counts"], config["threshold_n_sigma"])
    total_signal = float(config["background_mean_counts"]) + net_signal
    return {
        "case_id": parameter_set.get("case_id", "nominal"),
        "parameter": parameter_set.get("parameter", "nominal"),
        "factor": float(parameter_set.get("factor", 1.0)),
        "Q_dot_Bq_s": q_dot,
        "concentration_Bq_m3": concentration,
        "net_signal_counts": net_signal,
        "total_signal_counts": total_signal,
        "threshold_counts": threshold,
        "threshold_n_sigma": float(config["threshold_n_sigma"]),
        "threshold_crossing": bool(total_signal > threshold),
    }


def compute_sensitivity_metrics(nominal_result: dict[str, Any], modified_result: dict[str, Any]) -> dict[str, Any]:
    """Return percent-change sensitivity metrics for concentration and count signal."""
    def pct_change(name: str) -> float:
        base = float(nominal_result[name])
        modified = float(modified_result[name])
        if base == 0.0:
            return 0.0
        return 100.0 * (modified - base) / base

    return {
        **modified_result,
        "concentration_pct_change": pct_change("concentration_Bq_m3"),
        "net_signal_pct_change": pct_change("net_signal_counts"),
        "threshold_margin_counts": float(modified_result["total_signal_counts"]) - float(modified_result["threshold_counts"]),
    }


def export_sensitivity_table(results: list[dict[str, Any]]) -> pd.DataFrame:
    """Return sensitivity results as a table with units encoded in column names."""
    return pd.DataFrame(results)
