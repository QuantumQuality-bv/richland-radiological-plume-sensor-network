from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.sensitivity import (
    compute_sensitivity_metrics,
    export_sensitivity_table,
    one_at_a_time_parameter_sets,
    run_sensitivity_case,
)


def main() -> None:
    """Run Phase 7 one-at-a-time sensitivity and write CSV outputs with unit-labeled columns."""
    out_dir = ROOT / "data" / "processed" / "sensitivity_outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    nominal = run_sensitivity_case({"case_id": "nominal", "parameter": "nominal", "factor": 1.0, "config": {}})
    results = [compute_sensitivity_metrics(nominal, nominal)]
    for parameter_set in one_at_a_time_parameter_sets({}):
        modified = run_sensitivity_case(parameter_set)
        results.append(compute_sensitivity_metrics(nominal, modified))

    table = export_sensitivity_table(results)
    table.to_csv(out_dir / "sensitivity_table.csv", index=False)

    tornado = table[table["case_id"] != "nominal"].copy()
    tornado["absolute_concentration_pct_change"] = tornado["concentration_pct_change"].abs()
    tornado = tornado.sort_values("absolute_concentration_pct_change", ascending=False)
    tornado.to_csv(out_dir / "sensitivity_tornado.csv", index=False)

    print("Phase 7 sensitivity run complete.")
    print(f"Wrote: {out_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
