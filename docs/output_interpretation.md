# Output Interpretation

This note summarizes how to read the main generated outputs.

## Plume Outputs

- `data/processed/plume_outputs/plume_receptors.csv` contains receptor-level concentrations and wind-frame coordinates.
- `data/processed/plume_outputs/plume_grid.csv` contains gridded concentrations for contour visualization.
- `data/processed/plume_outputs/centerline_profile.csv` and `crosswind_profile.csv` provide profile slices used for validation and plotting.

## Detector Threshold Outputs

- `data/processed/detector_outputs/detector_timeseries.csv` contains per-detector count trajectories.
- `data/processed/detector_outputs/time_to_threshold.csv` records first crossing times for configured sigma thresholds.

## Network Comparison Outputs

- `data/processed/network_outputs/network_metrics.csv` provides the objective score and component metrics by candidate network.
- `data/processed/network_outputs/network_score_history.csv` records score decomposition across iterations.

## Source Reconstruction Outputs

- `data/processed/source_reconstruction_outputs/likelihood_grid.csv` and `noisy_likelihood_grid.csv` contain inverse-surface evaluations.
- `source_estimate.csv` and `noisy_source_estimate.csv` contain recovered source parameters for baseline and noisy cases.

## Sensitivity and Monte Carlo Outputs

- `data/processed/sensitivity_outputs/sensitivity_tornado.csv` contains one-at-a-time perturbation response metrics.
- `data/processed/monte_carlo_outputs/monte_carlo_results_final.csv` stores final-sample uncertainty results used for percentile tables and distribution plots.
