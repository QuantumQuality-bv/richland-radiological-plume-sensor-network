from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


EXPORTS = [
    ("data/processed/plume_outputs/plume_grid.csv", "plume_grid.csv"),
    ("data/processed/plume_outputs/centerline_profile.csv", "centerline_profile.csv"),
    ("data/processed/plume_outputs/crosswind_profile.csv", "crosswind_profile.csv"),
    ("data/processed/plume_outputs/plume_receptors.csv", "plume_receptors.csv"),
    ("data/processed/detector_outputs/detector_timeseries.csv", "detector_timeseries.csv"),
    ("data/processed/detector_outputs/time_to_threshold.csv", "time_to_threshold.csv"),
    ("data/processed/network_outputs/candidate_detector_map.csv", "candidate_detector_map.csv"),
    ("data/processed/network_outputs/network_metrics.csv", "network_metrics.csv"),
    ("data/processed/network_outputs/cost_coverage_trade.csv", "cost_coverage_trade.csv"),
    ("data/processed/source_reconstruction_outputs/likelihood_grid.csv", "likelihood_grid.csv"),
    ("data/processed/source_reconstruction_outputs/source_estimate.csv", "source_estimate.csv"),
    ("data/processed/source_reconstruction_outputs/noisy_likelihood_grid.csv", "noisy_likelihood_grid.csv"),
    ("data/processed/source_reconstruction_outputs/noisy_source_estimate.csv", "noisy_source_estimate.csv"),
    ("data/processed/source_reconstruction_outputs/noisy_loc_error_summary.csv", "noisy_loc_error_summary.csv"),
    ("data/processed/source_reconstruction_outputs/src_recon_noisy_summary.csv", "src_recon_noisy_summary.csv"),
    ("data/processed/sensitivity_outputs/sensitivity_tornado.csv", "sensitivity_tornado.csv"),
    ("data/processed/monte_carlo_outputs/monte_carlo_results_final.csv", "monte_carlo_results_final.csv"),
    ("data/processed/monte_carlo_outputs/loc_error_dist.csv", "loc_error_dist.csv"),
    ("data/processed/monte_carlo_outputs/detect_prob_summary.csv", "detect_prob_summary.csv"),
    ("data/processed/monte_carlo_outputs/monte_carlo_percentiles.csv", "monte_carlo_percentiles.csv"),
]


def main() -> None:
    """Copy stable CSV outputs into MATLAB export folder without recomputing physics."""
    out_dir = ROOT / "data" / "processed" / "matlab_exports"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_rows = []
    for source_rel, target_name in EXPORTS:
        source = ROOT / source_rel
        if not source.exists():
            raise FileNotFoundError(f"Missing required MATLAB export input: {source_rel}")
        target = out_dir / target_name
        shutil.copy2(source, target)
        manifest_rows.append({"source_file": source_rel, "matlab_export_file": f"data/processed/matlab_exports/{target_name}"})
    pd.DataFrame(manifest_rows).to_csv(out_dir / "matlab_export_manifest.csv", index=False)

    print("Phase 8 MATLAB input export complete.")
    print(f"Wrote: {out_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
