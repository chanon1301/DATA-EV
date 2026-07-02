"""Ingest the source EV Excel file into the versioned raw data zone."""
import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_FILE = PROJECT_ROOT / "EV Data Explorer 2025.xlsx"
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def ingest(source_file: Path = SOURCE_FILE, raw_dir: Path = RAW_DIR) -> Path:
    if not source_file.exists():
        raise FileNotFoundError(f"Source file not found: {source_file}")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    dest_file = raw_dir / f"ev_data_{timestamp}.xlsx"

    raw_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_file, dest_file)

    df = pd.read_excel(dest_file)
    print(f"Ingested: {dest_file.name}")
    print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    print(f"Columns: {df.columns.tolist()}")

    return dest_file


if __name__ == "__main__":
    ingest()
