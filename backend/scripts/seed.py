"""Thin entrypoint for seeding

Run via: python -m scripts.seed
"""

import os
import sys
from pathlib import Path

from application.ingestion.service import seed_library

BACKEND_ROOT = Path(__file__).resolve().parent.parent
DROP_FILE = BACKEND_ROOT / "data" / "Library.xml"
# FIXTURE = BACKEND_ROOT / "fixtures" / "sample_library.xml"


def resolve_data_path() -> Path:
    override = os.getenv("SEED_DATA")
    if override:
        path = Path(override).expanduser()
        if not path.exists():
            # Explicit pointer that's wrong -> fail clearly, no traceback.
            sys.exit(f"SEED_DATA points to a missing file: {path}")
        return path

    if DROP_FILE.exists():
        return DROP_FILE
    
    sys.exit(f"missing library file")

    # print(f"No {DROP_FILE} found — falling back to bundled sample ({FIXTURE.name}).")
    # return FIXTURE


if __name__ == "__main__":
    seed_library(resolve_data_path())
    print("Tables seeded / updated with library data")
