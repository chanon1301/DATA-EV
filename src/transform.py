"""Clean the ingested raw EV data and split it into historical vs projection sets."""
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

COLUMN_RENAME = {
    "region_country": "country",
    "Aggregate group": "aggregate_group",
}


def latest_raw_file(raw_dir: Path = RAW_DIR) -> Path:
    files = sorted(raw_dir.glob("ev_data_*.xlsx"))
    if not files:
        raise FileNotFoundError(f"No raw files found in {raw_dir}. Run ingest.py first.")
    return files[-1]


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=COLUMN_RENAME)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df = df.drop_duplicates()
    return df


def transform(raw_file: Path | None = None, processed_dir: Path = PROCESSED_DIR) -> dict[str, Path]:
    raw_file = raw_file or latest_raw_file()
    df = pd.read_excel(raw_file)
    df = clean(df)

    processed_dir.mkdir(parents=True, exist_ok=True)

    historical = df[df["category"] == "Historical"]
    projection = df[df["category"] == "Projection-STEPS"]

    out_paths = {
        "historical": processed_dir / "ev_historical.csv",
        "projection": processed_dir / "ev_projection.csv",
    }
    historical.to_csv(out_paths["historical"], index=False)
    projection.to_csv(out_paths["projection"], index=False)

    print(f"Source: {raw_file.name}")
    print(f"Historical rows: {len(historical)} -> {out_paths['historical'].name}")
    print(f"Projection rows: {len(projection)} -> {out_paths['projection'].name}")

    return out_paths


if __name__ == "__main__":
    transform()
