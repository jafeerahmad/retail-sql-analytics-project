"""Run the retail analytics workflow without overwriting existing input files."""
import argparse
from pathlib import Path

from src import build_db, generate_data, run_analysis

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
REQUIRED = [RAW / "customers.csv", RAW / "products.csv", RAW / "sales.csv"]


def main():
    parser = argparse.ArgumentParser(description="Generate/build/run the retail analytics project.")
    parser.add_argument("--generate-sample", action="store_true",
                        help="overwrite data/raw/*.csv with the built-in synthetic sample")
    args = parser.parse_args()

    present = [path.exists() for path in REQUIRED]
    if args.generate_sample or not any(present):
        generate_data.main()
    elif all(present):
        print("Using existing files in data/raw/ (not overwriting your dataset).")
    else:
        missing = [path.name for path in REQUIRED if not path.exists()]
        raise FileNotFoundError(
            "Some raw input files are missing: " + ", ".join(missing)
            + ". Restore the missing file(s), or use --generate-sample to replace all three with demo data."
        )

    build_db.main()
    run_analysis.main()


if __name__ == "__main__":
    main()
