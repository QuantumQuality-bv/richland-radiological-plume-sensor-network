"""Report table assembly helpers for generated synthetic pipeline outputs."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_csv_required(path: Path) -> pd.DataFrame:
    """Return a required CSV table; units are encoded in the file's column names."""
    if not path.exists():
        raise FileNotFoundError(f"Missing required CSV file: {path}")
    return pd.read_csv(path)


def write_table(df: pd.DataFrame, path: Path) -> None:
    """Write a report table CSV; units are encoded in column names."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def output_manifest(root: Path, relative_paths: list[str]) -> pd.DataFrame:
    """Return generated-output manifest with file sizes in bytes."""
    rows = []
    for rel in relative_paths:
        path = root / rel
        rows.append({"output_file": rel, "exists": path.exists(), "size_bytes": path.stat().st_size if path.exists() else 0})
    return pd.DataFrame(rows)


def assert_required_outputs(root: Path, relative_paths: list[str]) -> None:
    """Raise a clear error if required generated outputs are missing."""
    missing = [rel for rel in relative_paths if not (root / rel).exists()]
    if missing:
        missing_text = "\n".join(f"- {rel}" for rel in missing)
        raise FileNotFoundError(f"Missing required output file(s):\n{missing_text}")


def _column(df: pd.DataFrame, candidates: list[str]) -> str:
    """Return the first available column using case-insensitive fallback."""
    for name in candidates:
        if name in df.columns:
            return name
    lower_map = {col.lower(): col for col in df.columns}
    for name in candidates:
        match = lower_map.get(name.lower())
        if match is not None:
            return match
    raise KeyError(f"None of the expected columns exist: {candidates}")


def _baseline_rows(df: pd.DataFrame, scenario_id: str = "S1") -> pd.DataFrame:
    """Return baseline rows when scenario metadata is present; otherwise return all rows."""
    if "scenario_id" not in df.columns:
        return df
    baseline = df[df["scenario_id"] == scenario_id]
    return baseline if not baseline.empty else df


def plume_validation_targets(root: Path) -> pd.DataFrame:
    """Return selected plume validation targets from receptor outputs."""
    plume = _baseline_rows(read_csv_required(root / "data" / "processed" / "plume_outputs" / "plume_receptors.csv"))
    concentration_col = _column(plume, ["concentration_bq_m3", "concentration_Bq_m3"])
    receptor_col = _column(plume, ["receptor_id"])

    def row_for(receptor_id: str) -> pd.Series:
        rows = plume[plume[receptor_col] == receptor_id]
        if rows.empty:
            raise KeyError(f"Missing plume validation receptor: {receptor_id}")
        return rows.iloc[0]

    centerline = row_for("R001")
    crosswind = row_for("R002")
    upwind = row_for("R003")
    return pd.DataFrame(
        [
            {"quantity": "C_1000m_centerline_Bq_m3", "value": centerline[concentration_col], "module": "src/plume_gaussian.py", "output_file": "data/processed/plume_outputs/plume_receptors.csv"},
            {"quantity": "C_1000m_200m_crosswind_Bq_m3", "value": crosswind[concentration_col], "module": "src/plume_gaussian.py", "output_file": "data/processed/plume_outputs/plume_receptors.csv"},
            {"quantity": "C_upwind_Bq_m3", "value": upwind[concentration_col], "module": "src/plume_gaussian.py", "output_file": "data/processed/plume_outputs/plume_receptors.csv"},
        ]
    )


def detector_threshold_summary(root: Path) -> pd.DataFrame:
    """Return detector threshold-crossing summary table."""
    detector = _baseline_rows(read_csv_required(root / "data" / "processed" / "detector_outputs" / "time_to_threshold.csv"))
    return detector.copy()


def source_reconstruction_summary(root: Path) -> pd.DataFrame:
    """Return source reconstruction estimate summary table."""
    return read_csv_required(root / "data" / "processed" / "source_reconstruction_outputs" / "source_estimate.csv")


def validation_target_table(root: Path) -> pd.DataFrame:
    """Return selected validation targets with concentrations in Bq/m^3 and signals in counts."""
    plume_targets = plume_validation_targets(root)
    detector = _baseline_rows(read_csv_required(root / "data" / "processed" / "detector_outputs" / "detector_timeseries.csv"))
    detector_id_col = _column(detector, ["detector_id"])
    detector_peak = detector[(detector[detector_id_col] == "D002")].sort_values("total_signal_counts", ascending=False).iloc[0]
    rows = plume_targets.to_dict("records")
    rows.append(
        {"quantity": "D002_peak_total_signal_counts", "value": detector_peak["total_signal_counts"], "module": "src/detector_model.py", "output_file": "data/processed/detector_outputs/detector_timeseries.csv"}
    )
    return pd.DataFrame(
        rows
    )
