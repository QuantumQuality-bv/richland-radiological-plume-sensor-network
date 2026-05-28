from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.network_optimization import (
    DEFAULT_WEIGHTS,
    compare_network_designs,
    greedy_network_selection,
    score_network,
)


def _subset(candidates: pd.DataFrame, detector_ids: list[str]) -> pd.DataFrame:
    """Return candidate detector subset by identifier; cost is a dimensionless proxy."""
    return candidates[candidates["detector_id"].isin(detector_ids)].copy()


def _network_rows(network_id: str, detectors: pd.DataFrame) -> list[dict[str, object]]:
    """Return network definition rows with detector coordinates in meters."""
    if detectors.empty:
        return [{"network_id": network_id, "detector_id": None, "x_m": None, "y_m": None, "cost_proxy": 0.0, "network_role": "reference"}]
    rows = []
    for row in detectors.itertuples(index=False):
        rows.append(
            {
                "network_id": network_id,
                "detector_id": row.detector_id,
                "x_m": row.x_m,
                "y_m": row.y_m,
                "cost_proxy": row.cost_proxy,
                "network_role": "selected",
            }
        )
    return rows


def main() -> None:
    """Run Phase 5 network comparison and write cost/coverage CSV outputs."""
    synthetic_dir = ROOT / "data" / "synthetic"
    detector_dir = ROOT / "data" / "processed" / "detector_outputs"
    out_dir = ROOT / "data" / "processed" / "network_outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    candidates = pd.read_csv(synthetic_dir / "candidate_detectors.csv")
    detector_results = pd.read_csv(detector_dir / "time_to_threshold.csv")
    normalization = {
        "T_max_s": 1200.0,
        "C_max": 5.0,
        "sector_definition": {"n_sectors": 8, "source_x_m": 0.0, "source_y_m": 0.0},
    }

    def objective(subset: pd.DataFrame) -> dict[str, float]:
        return score_network(subset, detector_results, DEFAULT_WEIGHTS, normalization)

    n3_history = greedy_network_selection(candidates, 5, objective)
    n3_ids = str(n3_history.iloc[-1]["selected_detector_ids"]).split(";") if not n3_history.empty else []

    selected_n4: list[str] = []
    n4_rows = []
    for step in range(1, 6):
        best_id = None
        best_metrics = None
        best_score = -1.0
        for detector_id in candidates["detector_id"].tolist():
            if detector_id in selected_n4:
                continue
            trial = _subset(candidates, selected_n4 + [detector_id])
            if float(trial["cost_proxy"].sum()) > 3.6:
                continue
            metrics = objective(trial)
            if metrics["score"] > best_score or (metrics["score"] == best_score and (best_id is None or detector_id < best_id)):
                best_id = detector_id
                best_metrics = metrics
                best_score = metrics["score"]
        if best_id is None or best_metrics is None:
            break
        selected_n4.append(best_id)
        n4_rows.append({"network_family": "N4", "step": step, "added_detector_id": best_id, "selected_detector_ids": ";".join(selected_n4), **best_metrics})
    n4_history = pd.DataFrame(n4_rows)

    network_defs = []
    network_defs += _network_rows("N0", pd.DataFrame(columns=candidates.columns))
    network_defs += _network_rows("N1", _subset(candidates, ["D001", "D002", "D003", "D004", "D005"]))
    network_defs += _network_rows("N2", _subset(candidates, ["D001", "D002", "D005", "D018", "D019"]))
    network_defs += _network_rows("N3", _subset(candidates, n3_ids))
    network_defs += _network_rows("N4", _subset(candidates, selected_n4))
    network_definitions = pd.DataFrame(network_defs)
    network_definitions.to_csv(out_dir / "network_definitions.csv", index=False)

    network_metrics = compare_network_designs(network_definitions, detector_results)
    network_metrics.to_csv(out_dir / "network_metrics.csv", index=False)

    n3_history = n3_history.assign(network_family="N3") if not n3_history.empty else n3_history
    score_history = pd.concat([n3_history, n4_history], ignore_index=True)
    score_history.to_csv(out_dir / "network_score_history.csv", index=False)

    detector_map = candidates.copy()
    for network_id in ["N1", "N2", "N3", "N4"]:
        selected = set(network_definitions.loc[network_definitions["network_id"] == network_id, "detector_id"].dropna())
        detector_map[f"in_{network_id}"] = detector_map["detector_id"].isin(selected)
    detector_map.to_csv(out_dir / "candidate_detector_map.csv", index=False)

    trade_rows = [{"network_size": 0, "selected_detector_ids": "", **objective(pd.DataFrame(columns=candidates.columns))}]
    for _, row in n3_history.iterrows():
        ids = str(row["selected_detector_ids"]).split(";")
        trade_rows.append({"network_size": len(ids), "selected_detector_ids": row["selected_detector_ids"], **objective(_subset(candidates, ids))})
    pd.DataFrame(trade_rows).to_csv(out_dir / "cost_coverage_trade.csv", index=False)

    print("Phase 5 network comparison complete.")
    print(f"Wrote: {out_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
