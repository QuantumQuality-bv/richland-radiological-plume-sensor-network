from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.monte_carlo import (
    compute_percentile_summary,
    estimate_detection_probability,
    export_monte_carlo_outputs,
    run_monte_carlo,
    sample_uncertain_inputs,
)


def parse_args() -> argparse.Namespace:
    """Return command-line arguments; sample count is dimensionless."""
    parser = argparse.ArgumentParser(description="Run synthetic Monte Carlo uncertainty propagation.")
    parser.add_argument("--n-samples", type=int, default=500, help="Number of Monte Carlo samples.")
    parser.add_argument("--run-name", default="quick_check", help="Run label written into output rows.")
    parser.add_argument("--seed", type=int, default=20260513, help="Random seed.")
    return parser.parse_args()


def main() -> None:
    """Run Phase 7 Monte Carlo and write CSV outputs with unit-labeled columns."""
    args = parse_args()
    out_dir = ROOT / "data" / "processed" / "monte_carlo_outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "Q_dot_Bq_s": 8.333333333333334,
        "wind_speed_mps": 3.0,
        "wind_dir_deg": 0.0,
        "background_mean_counts": 7200.0,
        "background_sigma_counts": 84.85,
        "response_factor": 1.0e6,
        "threshold_n_sigma": 3.0,
        "x_m": 1000.0,
        "y_m": 0.0,
    }
    samples = sample_uncertain_inputs(config, args.n_samples, seed=args.seed)
    samples["run_name"] = args.run_name
    samples.to_csv(out_dir / "monte_carlo_samples.csv", index=False)
    samples.to_csv(out_dir / f"monte_carlo_samples_{args.run_name}.csv", index=False)

    results = run_monte_carlo(samples)
    results["run_name"] = args.run_name
    summary = compute_percentile_summary(results)
    summary["run_name"] = args.run_name
    export_monte_carlo_outputs(results, summary)
    results.to_csv(out_dir / f"monte_carlo_results_{args.run_name}.csv", index=False)
    summary.to_csv(out_dir / f"monte_carlo_percentiles_{args.run_name}.csv", index=False)

    detection_probability = estimate_detection_probability(results)
    pd.DataFrame(
        [
            {
                "run_name": args.run_name,
                "n_samples": args.n_samples,
                "detection_probability": detection_probability,
            }
        ]
    ).to_csv(out_dir / "detect_prob_summary.csv", index=False)
    results[["run_name", "sample_id", "localization_error_m"]].to_csv(out_dir / "loc_error_dist.csv", index=False)

    print("Phase 7 Monte Carlo run complete.")
    print(f"Wrote: {out_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
