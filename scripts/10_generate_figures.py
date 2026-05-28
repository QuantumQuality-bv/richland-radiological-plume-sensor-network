from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.ioff()

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.plotting import FINAL_FIGURES, generate_all_figures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic report figures.")
    parser.add_argument(
        "--profile",
        choices=["main", "all"],
        default="main",
        help="`main` generates final/main figures only; `all` also generates optional/supporting figures.",
    )
    return parser.parse_args()


def _write_markdown_manifest(manifest, path: Path) -> None:
    """Write a concise figure manifest for report integration."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Figure Manifest",
        "",
        "Final figures are generated from synthetic computational outputs by `scripts/10_generate_figures.py`.",
        "",
        "| Figure | Script | Input CSVs | Purpose | Report section | Status |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    seen = set()
    for item in FINAL_FIGURES:
        figure_id = item["figure_id"]
        if figure_id in seen:
            continue
        seen.add(figure_id)
        lines.append(
            f"| `{figure_id}` | `scripts/10_generate_figures.py` | `{item['inputs']}` | {item['purpose']} | {item['section']} | {item.get('status', 'final/main')} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """Generate final report-ready figures from processed synthetic outputs."""
    args = parse_args()
    include_optional = args.profile == "all"
    print(f"Figure profile: {args.profile}", flush=True)
    manifest = generate_all_figures(ROOT, include_optional=include_optional)
    figures_manifest = ROOT / "figures" / "figure_manifest.csv"
    figures_manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(figures_manifest, index=False)
    _write_markdown_manifest(manifest, ROOT / "docs" / "figure_manifest.md")

    print("Final figure generation complete.")
    for file_name in manifest["file"].drop_duplicates().sort_values():
        print(f"Wrote: {file_name}")
    print(f"Wrote: {figures_manifest.relative_to(ROOT)}")
    print("Wrote: docs/figure_manifest.md")


if __name__ == "__main__":
    main()
