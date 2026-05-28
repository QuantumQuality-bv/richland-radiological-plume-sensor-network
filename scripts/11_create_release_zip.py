from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ZIP = ROOT.parent / "richland-plume-sensor-network.zip"
PACKAGE_ROOT = "richland-plume-sensor-network"

EXCLUDED_DIRS = {
    ".git",
    ".idea",
    ".pytest_cache",
    ".venv",
    ".vscode",
    "__pycache__",
    "env",
    "venv",
}

EXCLUDED_SUFFIXES = {
    ".aux",
    ".bbl",
    ".blg",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".out",
    ".pyc",
    ".pyo",
    ".synctex.gz",
    ".toc",
}

EXCLUDED_NAMES = {
    ".DS_Store",
    "Thumbs.db",
}


def _is_excluded(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDED_DIRS:
        return True
    if path.name in EXCLUDED_NAMES:
        return True
    name = path.name.lower()
    return any(name.endswith(suffix) for suffix in EXCLUDED_SUFFIXES)


def create_zip(output_path: Path) -> None:
    """Create a release ZIP with POSIX-style archive paths."""
    output_path = output_path.resolve()
    if output_path.exists():
        output_path.unlink()
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(ROOT.rglob("*")):
            rel = path.relative_to(ROOT)
            if _is_excluded(rel):
                continue
            archive_name = Path(PACKAGE_ROOT, rel).as_posix()
            if path.is_dir():
                continue
            zf.write(path, archive_name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a clean release ZIP with portable archive paths.")
    parser.add_argument("--output", type=Path, default=DEFAULT_ZIP, help="Output ZIP path.")
    args = parser.parse_args()
    create_zip(args.output)
    print(f"Wrote: {args.output.resolve()}")


if __name__ == "__main__":
    main()
