from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.report_tables import (
    assert_required_outputs,
    detector_threshold_summary,
    output_manifest,
    plume_validation_targets,
    source_reconstruction_summary,
    validation_target_table,
    write_table,
)


REQUIRED_OUTPUTS = [
    "data/processed/input_summary.csv",
    "data/processed/core_validation_results.csv",
    "data/processed/plume_outputs/plume_receptors.csv",
    "data/processed/plume_outputs/plume_grid.csv",
    "data/processed/plume_outputs/centerline_profile.csv",
    "data/processed/plume_outputs/crosswind_profile.csv",
    "data/processed/plume_outputs/dispersion_comparison.csv",
    "data/processed/plume_outputs/puff_arrival_times.csv",
    "data/processed/detector_outputs/background_only_signals.csv",
    "data/processed/detector_outputs/detector_timeseries.csv",
    "data/processed/detector_outputs/threshold_crossings.csv",
    "data/processed/detector_outputs/false_positive_summary.csv",
    "data/processed/detector_outputs/time_to_threshold.csv",
    "data/processed/network_outputs/network_definitions.csv",
    "data/processed/network_outputs/network_metrics.csv",
    "data/processed/network_outputs/network_score_history.csv",
    "data/processed/network_outputs/candidate_detector_map.csv",
    "data/processed/network_outputs/cost_coverage_trade.csv",
    "data/processed/source_reconstruction_outputs/synthetic_observations.csv",
    "data/processed/source_reconstruction_outputs/candidate_source_grid.csv",
    "data/processed/source_reconstruction_outputs/least_squares_grid.csv",
    "data/processed/source_reconstruction_outputs/likelihood_grid.csv",
    "data/processed/source_reconstruction_outputs/noisy_likelihood_grid.csv",
    "data/processed/source_reconstruction_outputs/noisy_source_estimate.csv",
    "data/processed/source_reconstruction_outputs/noisy_loc_error_summary.csv",
    "data/processed/source_reconstruction_outputs/src_recon_noisy_summary.csv",
    "data/processed/source_reconstruction_outputs/source_estimate.csv",
    "data/processed/source_reconstruction_outputs/localization_error_summary.csv",
    "data/processed/sensitivity_outputs/sensitivity_table.csv",
    "data/processed/sensitivity_outputs/sensitivity_tornado.csv",
    "data/processed/monte_carlo_outputs/monte_carlo_samples.csv",
    "data/processed/monte_carlo_outputs/monte_carlo_results.csv",
    "data/processed/monte_carlo_outputs/monte_carlo_percentiles.csv",
    "data/processed/monte_carlo_outputs/detect_prob_summary.csv",
    "data/processed/monte_carlo_outputs/loc_error_dist.csv",
    "data/processed/matlab_exports/matlab_export_manifest.csv",
    "figures/figure_manifest.csv",
]


def _copy_table(source_rel: str, target: Path) -> None:
    """Copy a generated CSV report table with units preserved in column names."""
    source = ROOT / source_rel
    if not source.exists():
        raise FileNotFoundError(f"Missing required report input: {source_rel}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def main() -> None:
    """Build Phase 10 report tables from generated computational outputs."""
    tables_dir = ROOT / "report" / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    assert_required_outputs(ROOT, REQUIRED_OUTPUTS)

    write_table(output_manifest(ROOT, REQUIRED_OUTPUTS), tables_dir / "output_manifest.csv")
    _copy_table("data/processed/core_validation_results.csv", tables_dir / "core_validation_results.csv")
    write_table(plume_validation_targets(ROOT), tables_dir / "plume_validation_targets.csv")
    write_table(detector_threshold_summary(ROOT), tables_dir / "detector_threshold_summary.csv")
    write_table(source_reconstruction_summary(ROOT), tables_dir / "source_reconstruction_summary.csv")

    write_table(validation_target_table(ROOT), tables_dir / "validation_targets.csv")
    _copy_table("data/processed/detector_outputs/time_to_threshold.csv", tables_dir / "detector_time_to_threshold.csv")
    _copy_table("data/processed/network_outputs/network_metrics.csv", tables_dir / "network_metrics.csv")
    _copy_table("data/processed/network_outputs/network_metrics.csv", tables_dir / "network_comparison_report_table.csv")
    _copy_table("data/processed/source_reconstruction_outputs/source_estimate.csv", tables_dir / "source_estimate.csv")
    _copy_table("data/processed/source_reconstruction_outputs/localization_error_summary.csv", tables_dir / "localization_error_summary.csv")
    _copy_table("data/processed/source_reconstruction_outputs/src_recon_noisy_summary.csv", tables_dir / "src_recon_noisy_summary.csv")
    _copy_table("data/processed/sensitivity_outputs/sensitivity_tornado.csv", tables_dir / "sensitivity_tornado.csv")
    _copy_table("data/processed/sensitivity_outputs/sensitivity_tornado.csv", tables_dir / "sensitivity_report_table.csv")
    _copy_table("data/processed/monte_carlo_outputs/monte_carlo_percentiles.csv", tables_dir / "monte_carlo_percentiles.csv")
    _copy_table("data/processed/monte_carlo_outputs/detect_prob_summary.csv", tables_dir / "detect_prob_summary.csv")

    traceability = pd.DataFrame(
        [
            {"report_section": "Synthetic source and plume model", "module": "src/plume_gaussian.py", "output_file": "data/processed/plume_outputs/plume_receptors.csv"},
            {"report_section": "Detector response simulation", "module": "src/detector_model.py", "output_file": "data/processed/detector_outputs/detector_timeseries.csv"},
            {"report_section": "Sensor network comparison", "module": "src/network_optimization.py", "output_file": "data/processed/network_outputs/network_metrics.csv"},
            {"report_section": "Source reconstruction and uncertainty", "module": "src/source_reconstruction.py", "output_file": "data/processed/source_reconstruction_outputs/likelihood_grid.csv"},
            {"report_section": "Sensitivity and Monte Carlo", "module": "src/monte_carlo.py", "output_file": "data/processed/monte_carlo_outputs/monte_carlo_percentiles.csv"},
        ]
    )
    write_table(traceability, tables_dir / "module_output_traceability.csv")

    print("Phase 10 report table build complete.")
    print(f"Wrote: {tables_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
