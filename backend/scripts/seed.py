"""Thin entrypoint for seeding — resolves the data path and runs the use case.

Logic lives in ``application.ingestion.service.seed_library``. Run via:
    python -m scripts.seed
"""

import os
from pathlib import Path

from application.ingestion.service import seed_library

DEFAULT_DATA = (
    Path(__file__).resolve().parent.parent / "fixtures" / "sample_library.xml"
)
DATA = Path(os.getenv("SEED_DATA", DEFAULT_DATA))


if __name__ == "__main__":
    seed_library(DATA)
    print("Tables seeded / updated with library data")
