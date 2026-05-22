import argparse
import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from handlers.albums_search_by_artists import main
from resources.music_library import find_near_duplicate_artists, parse_library

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("run")

SOURCE = "music_app"  # "music_app" | "folders"
TOP_N_ARTISTS = 50
MIN_TRACK_PLAYS = 1
MIN_ARTIST_PLAYS = 5
DEFAULT_LIBRARY_PATH = Path("~/Music/Library.xml")


def resolve_library_path(cli_path: str | None) -> Path:
    if cli_path:
        return Path(cli_path).expanduser()
    env_path = os.environ.get("MUSIC_LIBRARY_XML")
    if env_path:
        return Path(env_path).expanduser()
    return DEFAULT_LIBRARY_PATH.expanduser()


def artists_from_music_app(library_path: Path) -> list[str]:
    parsed = parse_library(
        library_path,
        min_track_plays=MIN_TRACK_PLAYS,
        min_artist_plays=MIN_ARTIST_PLAYS,
    )

    dupes = find_near_duplicate_artists(parsed.keys())
    if dupes:
        logger.warning("Near-duplicate Album Artists detected — clean up in Music.app:")
        for group in dupes:
            logger.warning("  %s", " | ".join(group))

    top = list(parsed.keys())[:TOP_N_ARTISTS]
    logger.info("Top %d artists by play count selected", len(top))
    return top


def artists_from_folders() -> list[str]:
    folder = os.path.expanduser(
        "~/Music/iTunes/Previous iTunes Libraries/Previous iTunes Libraries/iTunes Media/Music"
    )
    return os.listdir(folder)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build album list from Music.app library.")
    parser.add_argument(
        "library_positional",
        nargs="?",
        help="Path to Music.app Library.xml (positional shorthand for --library).",
    )
    parser.add_argument(
        "--library",
        help="Path to Music.app Library.xml. Overrides MUSIC_LIBRARY_XML env var.",
    )
    return parser.parse_args()


def write_results(results) -> None:
    output_path = Path("./data/albums.json")
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w") as outfile:
            json.dump(results, outfile, indent=2)
        logger.info("Saved to %s", output_path)
    except OSError as exc:
        logger.error("Could not write %s: %s — falling back to ./tempOutput.json", output_path, exc)
        with open("./tempOutput.json", "w") as outfile:
            json.dump(results, outfile, indent=2)


def main_cli() -> None:
    args = parse_args()

    if SOURCE == "music_app":
        library_path = resolve_library_path(args.library or args.library_positional)
        logger.info("Reading library: %s", library_path)
        artists = artists_from_music_app(library_path)
    elif SOURCE == "folders":
        artists = artists_from_folders()
    else:
        raise ValueError(f"Unknown SOURCE: {SOURCE!r}")

    event = {"body": json.dumps({"artists": artists})}
    response = main(event=event, context={})
    results = json.loads(response["body"])
    write_results(results)


if __name__ == "__main__":
    main_cli()
