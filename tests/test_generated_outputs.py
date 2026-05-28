from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_CSVS = [
    "data/processed/plume_outputs/plume_receptors.csv",
    "data/processed/plume_outputs/plume_grid.csv",
    "data/processed/plume_outputs/centerline_profile.csv",
    "data/processed/plume_outputs/crosswind_profile.csv",
    "data/processed/detector_outputs/detector_timeseries.csv",
    "data/processed/detector_outputs/time_to_threshold.csv",
    "data/processed/network_outputs/network_metrics.csv",
    "data/processed/source_reconstruction_outputs/likelihood_grid.csv",
    "data/processed/source_reconstruction_outputs/noisy_likelihood_grid.csv",
    "data/processed/source_reconstruction_outputs/src_recon_noisy_summary.csv",
    "data/processed/source_reconstruction_outputs/source_estimate.csv",
    "data/processed/sensitivity_outputs/sensitivity_tornado.csv",
    "data/processed/monte_carlo_outputs/monte_carlo_results_final.csv",
    "report/tables/output_manifest.csv",
    "report/tables/module_output_traceability.csv",
]


FIGURE_BASES = [
    "plume_log_contour",
    "centerline_profile",
    "crosswind_profile",
    "detector_timeseries",
    "network_metrics",
    "src_recon_likelihood",
    "src_recon_error_dist",
    "sensitivity_tornado",
    "mc_uncertainty_summary",
]

OPTIONAL_FIGURE_BASES = [
    "detection_probability_by_network",
    "mc_conc_dist",
    "mc_ttd_dist",
    "mc_loc_error_dist",
]


def test_required_generated_csvs_exist_and_are_nonempty():
    for rel_path in REQUIRED_CSVS:
        path = ROOT / rel_path
        assert path.exists(), rel_path
        assert path.stat().st_size > 0, rel_path


def test_required_figures_exist_and_are_nonempty():
    for basename in FIGURE_BASES:
        for ext in ("pdf", "png"):
            path = ROOT / "figures" / f"{basename}.{ext}"
            assert path.exists(), str(path.relative_to(ROOT))
            assert path.stat().st_size > 0, str(path.relative_to(ROOT))


def test_optional_figures_are_consistent_if_present():
    for basename in OPTIONAL_FIGURE_BASES:
        pdf_path = ROOT / "figures" / f"{basename}.pdf"
        png_path = ROOT / "figures" / f"{basename}.png"
        assert pdf_path.exists() == png_path.exists(), str(pdf_path.relative_to(ROOT))
        if pdf_path.exists():
            assert pdf_path.stat().st_size > 0, str(pdf_path.relative_to(ROOT))
            assert png_path.stat().st_size > 0, str(png_path.relative_to(ROOT))


def test_output_data_sanity_checks():
    plume = pd.read_csv(ROOT / "data/processed/plume_outputs/plume_receptors.csv")
    concentration_col = "concentration_bq_m3" if "concentration_bq_m3" in plume.columns else "concentration_Bq_m3"
    assert (plume[concentration_col] >= 0.0).all()
    assert float(plume.loc[plume["receptor_id"] == "R003", concentration_col].iloc[0]) == 0.0
    assert float(plume.loc[plume["receptor_id"] == "R002", concentration_col].iloc[0]) < float(
        plume.loc[plume["receptor_id"] == "R001", concentration_col].iloc[0]
    )

    centerline = pd.read_csv(ROOT / "data/processed/plume_outputs/centerline_profile.csv")
    c_col = "concentration_bq_m3" if "concentration_bq_m3" in centerline.columns else "concentration_Bq_m3"
    after_max = centerline.loc[centerline[c_col].idxmax() :, c_col].to_numpy()
    assert all(after_max[i] >= after_max[i + 1] for i in range(len(after_max) - 1))

    thresholds = pd.read_csv(ROOT / "data/processed/detector_outputs/time_to_threshold.csv")
    d001 = thresholds[(thresholds["detector_id"] == "D001") & (thresholds["n_sigma"] == 3.0)]
    assert not d001.empty
    assert pd.notna(d001.iloc[0]["first_threshold_crossing_s"])

    estimate = pd.read_csv(ROOT / "data/processed/source_reconstruction_outputs/source_estimate.csv").iloc[0]
    assert abs(float(estimate["estimated_x_m"])) <= 1.0e-6
    assert abs(float(estimate["estimated_y_m"])) <= 1.0e-6

    noisy = pd.read_csv(ROOT / "data/processed/source_reconstruction_outputs/src_recon_noisy_summary.csv").iloc[0]
    assert 20.0 <= float(noisy["localization_error_m"]) <= 100.0

    mc = pd.read_csv(ROOT / "data/processed/monte_carlo_outputs/monte_carlo_results_final.csv")
    assert len(mc) == 5000
    assert (mc["localization_error_m"] >= 0.0).all()

    network = pd.read_csv(ROOT / "data/processed/network_outputs/network_metrics.csv")
    assert network["P_detect"].between(0.0, 1.0).all()


def test_figure_manifest_points_to_existing_files():
    manifest = pd.read_csv(ROOT / "figures/figure_manifest.csv")
    assert not manifest.empty
    for rel_path in manifest["file"]:
        assert (ROOT / rel_path).exists(), rel_path
