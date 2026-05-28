# Synthetic Radiological Plume Modeling and Sensor Network Analysis

A reproducible Python/MATLAB modeling package for synthetic Gaussian plume calculations, detector response simulation, sensor network comparison, source reconstruction, and uncertainty analysis in a public Richland-area coordinate domain.

This repository uses synthetic source terms, detector locations, meteorology, and coordinate systems to demonstrate a reproducible plume/sensor-network modeling workflow. The outputs are computational examples for model development, visualization, uncertainty analysis, and source-reconstruction testing.

## Repository Structure

- `config/` - assumptions and run configuration.
- `data/synthetic/` - generated synthetic input CSVs.
- `data/processed/` - regenerated computational outputs.
- `src/` - plume, detector, network, reconstruction, sensitivity, Monte Carlo, plotting, and report-table modules.
- `scripts/` - ordered pipeline entry points.
- `matlab/` - MATLAB helpers for reading exported CSVs and regenerating figures.
- `figures/` - final review figures in PDF and PNG.
- `report/tables/` - generated report-ready CSV tables.
- `docs/` - figure and bibliography audit manifests.
- `tests/` - unit, integration, output, and data sanity tests.

## Setup

Use Python 3.11.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Build Commands

Run the full pipeline from the repository root:

```bash
make all
```

On Windows, GNU Make may be available as `gmake`:

```powershell
gmake all PYTHON=.\.venv\Scripts\python.exe
```

Other useful targets:

```bash
make clean
make figures
make test
```

Equivalent script sequence:

Use `make all` for the full build. Individual scripts can also be run from `scripts/` in numeric order; the final Monte Carlo command is `python scripts/07_run_monte_carlo.py --n-samples 5000 --run-name final`.

## Expected Outputs

The build regenerates:

- plume receptor, grid, profile, dispersion, and puff CSVs under `data/processed/plume_outputs/`
- detector time-series and threshold-crossing CSVs under `data/processed/detector_outputs/`
- network metric and detector-map CSVs under `data/processed/network_outputs/`
- source reconstruction likelihood and estimate CSVs under `data/processed/source_reconstruction_outputs/`
- sensitivity and Monte Carlo CSVs under `data/processed/sensitivity_outputs/` and `data/processed/monte_carlo_outputs/`
- MATLAB-ready CSVs under `data/processed/matlab_exports/`
- final figures under `figures/`
- report tables under `report/tables/`
- manifests under `docs/figure_manifest.md`, `figures/figure_manifest.csv`, and `docs/bibliography_audit.md`

## Figures

Final figure basenames include:

- `plume_log_contour`
- `centerline_profile`
- `crosswind_profile`
- `detector_timeseries`
- `network_metrics`
- `detection_probability_by_network`
- `src_recon_likelihood`
- `src_recon_error_dist`
- `sensitivity_tornado`
- `mc_conc_dist`
- `mc_ttd_dist`
- `mc_loc_error_dist`
- `mc_uncertainty_summary`

Each is written as PDF and PNG in `figures/`.

## Report Status

The repository currently freezes the computational pipeline, generated tables, and figure outputs. The final report will be written from these frozen outputs.

## License

See `LICENSE`.

## Tests

```bash
python -m pytest -q
```

The output file `test_run_output.txt` records the latest test run result.
