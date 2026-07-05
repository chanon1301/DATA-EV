"""Validate cleaned EV data before it gets loaded into DuckDB."""
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

REQUIRED_COLUMNS = [
    "country", "category", "parameter", "mode",
    "powertrain", "year", "unit", "value", "aggregate_group",
]

ALLOWED_CATEGORY = {"Historical", "Projection-STEPS"}
ALLOWED_POWERTRAIN = {
    "EV", "BEV", "PHEV", "FCEV",
    "Publicly available slow", "Publicly available fast",
}

FILES = {
    "historical": PROCESSED_DIR / "ev_historical.csv",
    "projection": PROCESSED_DIR / "ev_projection.csv",
}


class ValidationError(Exception):
    pass


def validate_dataframe(df: pd.DataFrame, name: str) -> list[str]:
    errors = []

    missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_cols:
        errors.append(f"[{name}] missing columns: {missing_cols}")
        return errors  # further checks assume columns exist

    if df.empty:
        errors.append(f"[{name}] dataframe is empty")

    null_counts = df[REQUIRED_COLUMNS].isnull().sum()
    for col, count in null_counts.items():
        if count > 0:
            errors.append(f"[{name}] column '{col}' has {count} null value(s)")

    dup_count = df.duplicated().sum()
    if dup_count > 0:
        errors.append(f"[{name}] found {dup_count} duplicate row(s)")

    bad_category = set(df["category"].unique()) - ALLOWED_CATEGORY
    if bad_category:
        errors.append(f"[{name}] unexpected category value(s): {bad_category}")

    bad_powertrain = set(df["powertrain"].unique()) - ALLOWED_POWERTRAIN
    if bad_powertrain:
        errors.append(f"[{name}] unexpected powertrain value(s): {bad_powertrain}")

    if not df["year"].between(2010, 2035).all():
        errors.append(f"[{name}] found year value(s) outside expected range 2010-2035")

    if (df["value"] < 0).any():
        errors.append(f"[{name}] found negative value(s) in 'value' column")

    return errors


def validate(files: dict[str, Path] = FILES) -> None:
    all_errors = []

    for name, path in files.items():
        if not path.exists():
            raise FileNotFoundError(f"{path} not found. Run transform.py first.")
        df = pd.read_csv(path)
        errors = validate_dataframe(df, name)
        all_errors.extend(errors)
        print(f"[{name}] checked {len(df)} rows, {len(errors)} issue(s) found")

    if all_errors:
        for err in all_errors:
            print(f"  - {err}")
        raise ValidationError(f"Validation failed with {len(all_errors)} issue(s)")

    print("All checks passed.")


if __name__ == "__main__":
    validate()
