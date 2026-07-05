"""Load cleaned EV data (from transform.py) into a DuckDB database."""
from pathlib import Path

import duckdb
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DB_PATH = PROJECT_ROOT / "data" / "ev_data.duckdb"

TABLES = {
    "historical": PROCESSED_DIR / "ev_historical.csv",
    "projection": PROCESSED_DIR / "ev_projection.csv",
}


def load(db_path: Path = DB_PATH, tables: dict[str, Path] = TABLES) -> None:
    con = duckdb.connect(str(db_path))

    for table_name, csv_path in tables.items():
        if not csv_path.exists():
            raise FileNotFoundError(f"{csv_path} not found. Run transform.py first.")
        df = pd.read_csv(csv_path)
        con.register("df_tmp", df)
        con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df_tmp")
        count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"Loaded table '{table_name}': {count} rows")

    con.close()
    print(f"Database ready at: {db_path}")


if __name__ == "__main__":
    load()
