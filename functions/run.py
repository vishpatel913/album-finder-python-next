import argparse
import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from handlers.albums_search_by_artists import main
from resources.music_library import (
    find_near_duplicate_artists,
    parse_library,
    snapshot_library,
)

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("run")

SOURCE = "music_app"  # "music_app" | "folders"
TOP_N_ARTISTS = 50
MIN_TRACK_PLAYS = 1
MIN_ARTIST_PLAYS = 5
# Repo root: functions/run.py -> functions -> root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
# Default local dump location (gitignored): drop Library.xml in dumps/.
DEFAULT_LIBRARY_PATH = PROJECT_ROOT / "dumps" / "Library.xml"


def resolve_library_path(cli_path: str | None) -> Path:
    """CLI path wins, then MUSIC_LIBRARY_XML, then the gitignored dumps/ folder.

    Relative paths resolve against the project root, not the cwd.
    """
    if cli_path:
        return Path(cli_path).expanduser()
    env_path = os.environ.get("MUSIC_LIBRARY_XML")
    if env_path:
        path = Path(env_path).expanduser()
        return path if path.is_absolute() else (PROJECT_ROOT / path)
    return DEFAULT_LIBRARY_PATH


def artists_from_music_app(library_path: Path) -> list[str]:
    snapshot_library(library_path)
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
    parser.add_argument(
        "--enrich-all",
        action="store_true",
        help="Batch-fetch Spotify data for artists with non-compilation albums, then "
        "exit. Idempotent — only fetches artists not already cached.",
    )
    parser.add_argument(
        "--enrich-interactive",
        action="store_true",
        help="Like --enrich-all but prompt yes/no per artist. Needs a TTY: run via "
        "`docker compose exec api python run.py --enrich-interactive`.",
    )
    return parser.parse_args()


def enrich_all_cli(library_path: Path) -> None:
    """Populate the Spotify cache for the whole library (CLI entry point).

    Reuses the API's creds/timeout/cache wiring so behaviour matches the
    /api/spotify/enrich-all endpoint exactly.
    """
    from api.deps import cache_path, get_spotify
    from resources.artist_resolver import ArtistResolver
    from resources.music_library import enrichable_artist_names

    parsed = parse_library(library_path)
    resolver = ArtistResolver(get_spotify(), cache_path=cache_path())
    names = enrichable_artist_names(parsed)
    logger.info(
        "Enriching %d artists with non-compilation albums (%d compilation-only skipped, "
        "cached ones skipped too)…",
        len(names),
        len(parsed) - len(names),
    )
    results = resolver.resolve_many(names)
    resolver.save()
    matched = sum(1 for v in results.values() if v and v.get("id"))
    logger.info("Done: %d/%d artists matched on Spotify", matched, len(names))


def enrich_interactive_cli(library_path: Path) -> None:
    """Prompt yes/no per artist before fetching from Spotify.

    Only considers artists with non-compilation albums that aren't already
    cached. Saves after every 'yes' so it's safe to quit and resume.
    """
    from api.deps import cache_path, get_spotify
    from resources.artist_resolver import ArtistResolver
    from resources.music_library import enrichable_artist_names

    parsed = parse_library(library_path)
    resolver = ArtistResolver(get_spotify(), cache_path=cache_path())
    candidates = [
        name
        for name in enrichable_artist_names(parsed)
        if not (resolver.get_cached(name) or {}).get("id")
    ]
    total = len(candidates)
    if not total:
        logger.info("Nothing to do — all enrichable artists are already cached.")
        return

    print(f"\n{total} artists to consider.  [y]es  [n]o (default)  [a]ll remaining  [q]uit\n")
    auto_yes = False
    matched = 0
    try:
        for i, name in enumerate(candidates, 1):
            if auto_yes:
                choice = "y"
            else:
                choice = input(f"[{i}/{total}] Enrich \"{name}\"? [y/n/a/q] ").strip().lower()
            if choice in ("q", "quit"):
                print("Stopping early.")
                break
            if choice in ("a", "all"):
                auto_yes, choice = True, "y"
            if choice not in ("y", "yes"):
                continue  # empty / n / anything else → skip
            entry = resolver.resolve(name)
            resolver.save()  # persist after each yes → resumable
            if entry and entry.get("id"):
                matched += 1
                print(f"      ✓ {entry['display_name']}  (popularity {entry.get('popularity')})")
            else:
                print("      ✗ no Spotify match")
    except (EOFError, KeyboardInterrupt):
        print("\nInterrupted — progress saved.")
    resolver.save()
    logger.info("Interactive enrich finished: %d matched this session.", matched)


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

    if args.enrich_all or args.enrich_interactive:
        library_path = resolve_library_path(args.library or args.library_positional)
        logger.info("Reading library: %s", library_path)
        if args.enrich_interactive:
            enrich_interactive_cli(library_path)
        else:
            enrich_all_cli(library_path)
        return

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
