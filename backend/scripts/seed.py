"""Thin entrypoint for seeding

Run via: python -m scripts.seed
"""

import os
import sys
from pathlib import Path

from application.ingestion.service import seed_library


def resolve_data_path() -> Path:
    override = os.getenv("MUSIC_LIBRARY_PATH")
    if override:
        path = Path(override).expanduser()
        if not path.exists():
            # Explicit pointer that's wrong -> fail clearly, no traceback.
            sys.exit(f"MUSIC_LIBRARY_PATH points to a missing file: {path}")
        return path

    sys.exit("MUSIC_LIBRARY_PATH path is missing in env")


if __name__ == "__main__":
    seed_library(resolve_data_path())
    print("Tables seeded / updated with library data")
