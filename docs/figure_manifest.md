# Figure Manifest

Final figures are generated from synthetic computational outputs by `scripts/10_generate_figures.py`.

| Figure | Script | Input CSVs | Purpose | Report section | Status |
| --- | --- | --- | --- | --- | --- |
| `plume_log_contour` | `scripts/10_generate_figures.py` | `data/processed/plume_outputs/plume_grid.csv; data/synthetic/synthetic_receptors.csv` | Log-scaled Gaussian plume concentration field with validation receptors. | Synthetic source and plume model | final/main |
| `centerline_profile` | `scripts/10_generate_figures.py` | `data/processed/plume_outputs/centerline_profile.csv` | Downwind centerline concentration profile. | Synthetic source and plume model | final/main |
| `crosswind_profile` | `scripts/10_generate_figures.py` | `data/processed/plume_outputs/crosswind_profile.csv` | Crosswind concentration profile at the baseline downwind distance. | Synthetic source and plume model | final/main |
| `detector_timeseries` | `scripts/10_generate_figures.py` | `data/processed/detector_outputs/detector_timeseries.csv; data/processed/detector_outputs/time_to_threshold.csv` | Detector count time series with synthetic threshold crossings. | Detector response simulation | final/main |
| `network_metrics` | `scripts/10_generate_figures.py` | `data/processed/network_outputs/network_metrics.csv` | Comparison of score, probability, cost proxy, and wind-sector coverage. | Sensor network comparison | final/main |
| `detection_probability_by_network` | `scripts/10_generate_figures.py` | `data/processed/network_outputs/network_metrics.csv` | Detection probability by candidate network. | Sensor network comparison | optional/supporting |
| `src_recon_likelihood` | `scripts/10_generate_figures.py` | `data/processed/source_reconstruction_outputs/noisy_likelihood_grid.csv` | Noisy synthetic source reconstruction objective surface. | Source reconstruction and uncertainty | final/main |
| `src_recon_error_dist` | `scripts/10_generate_figures.py` | `data/processed/monte_carlo_outputs/loc_error_dist.csv` | Monte Carlo localization error distribution. | Source reconstruction and uncertainty | final/main |
| `sensitivity_tornado` | `scripts/10_generate_figures.py` | `data/processed/sensitivity_outputs/sensitivity_tornado.csv` | One-at-a-time concentration sensitivity tornado chart. | Sensitivity and Monte Carlo | final/main |
| `mc_conc_dist` | `scripts/10_generate_figures.py` | `data/processed/monte_carlo_outputs/monte_carlo_results_final.csv` | Final Monte Carlo concentration distribution. | Sensitivity and Monte Carlo | optional/supporting |
| `mc_ttd_dist` | `scripts/10_generate_figures.py` | `data/processed/monte_carlo_outputs/monte_carlo_results_final.csv` | Final Monte Carlo time-to-threshold distribution. | Sensitivity and Monte Carlo | optional/supporting |
| `mc_loc_error_dist` | `scripts/10_generate_figures.py` | `data/processed/monte_carlo_outputs/monte_carlo_results_final.csv` | Final Monte Carlo localization error distribution. | Sensitivity and Monte Carlo | optional/supporting |
| `mc_uncertainty_summary` | `scripts/10_generate_figures.py` | `data/processed/monte_carlo_outputs/monte_carlo_results_final.csv` | Three-panel Monte Carlo uncertainty summary. | Sensitivity and Monte Carlo | final/main |
