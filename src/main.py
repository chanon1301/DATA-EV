"""Run the full EV data pipeline: ingest -> transform -> validate -> load."""
import sys

from ingest import ingest
from transform import transform
from validate import validate, ValidationError
from Load import load


def run_pipeline() -> None:
    print("=== 1. Ingest ===")
    ingest()

    print("\n=== 2. Transform ===")
    transform()

    print("\n=== 3. Validate ===")
    try:
        validate()
    except ValidationError as e:
        print(f"\nPipeline stopped: {e}")
        sys.exit(1)

    print("\n=== 4. Load ===")
    load()

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()
