from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.detector_model import (
    evaluate_detector_network_timeseries,
    false_positive_rate,
    simulate_background,
    threshold_level,
    time_to_first_threshold_crossing,
)


def main() -> None:
    """Run Phase 4 detector simulation and write count-based CSV outputs."""
    synthetic_dir = ROOT / "data" / "synthetic"
    plume_dir = ROOT / "data" / "processed" / "plume_outputs"
    out_dir = ROOT / "data" / "processed" / "detector_outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    plume_timeseries = pd.read_csv(plume_dir / "puff_detector_timeseries.csv")
    backgrounds = pd.read_csv(synthetic_dir / "detector_backgrounds.csv")
    detectors = pd.read_csv(synthetic_dir / "candidate_detectors.csv")
    baseline_backgrounds = backgrounds[backgrounds["scenario_id"] == "S1"].copy()
    time_grid = sorted(plume_timeseries["time_s"].unique().tolist())

    background_rows = []
    for bg in baseline_backgrounds.itertuples(index=False):
        values = simulate_background(
            bg.background_mean_counts,
            bg.background_sigma_counts,
            len(time_grid),
            seed=int(bg.seed),
            model=str(bg.noise_model),
        )
        threshold_3 = threshold_level(bg.background_mean_counts, bg.background_sigma_counts, 3.0)
        threshold_5 = threshold_level(bg.background_mean_counts, bg.background_sigma_counts, 5.0)
        for time_s, value in zip(time_grid, values):
            background_rows.append(
                {
                    "scenario_id": bg.scenario_id,
                    "detector_id": bg.detector_id,
                    "time_s": time_s,
                    "background_counts": value,
                    "threshold_3sigma_counts": threshold_3,
                    "threshold_5sigma_counts": threshold_5,
                    "threshold_crossing_3sigma": value > threshold_3,
                    "threshold_crossing_5sigma": value > threshold_5,
                }
            )
    background_only = pd.DataFrame(background_rows)
    background_only.to_csv(out_dir / "background_only_signals.csv", index=False)

    detector_timeseries = evaluate_detector_network_timeseries(plume_timeseries, backgrounds, detectors)
    detector_timeseries.to_csv(out_dir / "detector_timeseries.csv", index=False)

    crossing_rows = []
    time_rows = []
    false_positive_rows = []
    for detector_id, group in detector_timeseries.groupby("detector_id", sort=True):
        bg_group = background_only[background_only["detector_id"] == detector_id]
        for n_sigma, threshold_col, crossing_col in [
            (3.0, "threshold_3sigma_counts", "threshold_crossing_3sigma"),
            (5.0, "threshold_5sigma_counts", "threshold_crossing_5sigma"),
        ]:
            threshold = float(group[threshold_col].iloc[0])
            first_time = time_to_first_threshold_crossing(group["time_s"], group["total_signal_counts"], threshold)
            time_rows.append(
                {
                    "scenario_id": group["scenario_id"].iloc[0],
                    "detector_id": detector_id,
                    "n_sigma": n_sigma,
                    "first_threshold_crossing_s": first_time,
                    "threshold_counts": threshold,
                }
            )
            false_rate = false_positive_rate(bg_group["background_counts"], threshold)
            false_positive_rows.append(
                {
                    "scenario_id": "S1",
                    "detector_id": detector_id,
                    "n_sigma": n_sigma,
                    "false_positive_rate": false_rate,
                    "n_steps": len(bg_group),
                }
            )
            for row in group.itertuples(index=False):
                crossing_rows.append(
                    {
                        "scenario_id": row.scenario_id,
                        "detector_id": detector_id,
                        "time_s": row.time_s,
                        "n_sigma": n_sigma,
                        "threshold_counts": threshold,
                        "total_signal_counts": row.total_signal_counts,
                        "threshold_crossing": bool(getattr(row, crossing_col)),
                    }
                )

    pd.DataFrame(crossing_rows).to_csv(out_dir / "threshold_crossings.csv", index=False)
    pd.DataFrame(false_positive_rows).to_csv(out_dir / "false_positive_summary.csv", index=False)
    pd.DataFrame(time_rows).to_csv(out_dir / "time_to_threshold.csv", index=False)

    print("Phase 4 detector simulation complete.")
    print(f"Wrote: {out_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
