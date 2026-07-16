import re
import unicodedata
from collections import defaultdict

_FEATURED_RE = re.compile(
    r"[\(\[]\s*(?:featuring|feat\.?|ft\.?)\s+(?P<artists>[^)\]]+?)\s*[\)\]]",
    re.IGNORECASE,
)
_FEATURED_SPLIT_RE = re.compile(r"\s*(?:,|&|\band\b)\s*", re.IGNORECASE)

_GREATEST_HITS_RE = re.compile(
    r"greatest hits|best of|the best|\bthe hits\b|\bhits\b|b-sides|anthology|"
    r"essential|definitive|collection|#1'?s|number ones|ultimate",
    re.IGNORECASE,
)


def extract_featured_artists_from_name(title: str | None) -> list[str] | None:
    """Return the raw featured-artist text from a track title, or None."""
    if not title:
        return None
    match = _FEATURED_RE.search(title)
    if not match:
        return None
    featured = match.group("artists").strip() or None
    if not featured:
        return []
    return [p.strip() for p in _FEATURED_SPLIT_RE.split(featured) if p.strip()]


def _normalise_artist_name(name: str) -> str:
    # NFKD + ASCII fold strips accents; casefold + whitespace collapse
    # catches the "Beyoncé" vs "Beyonce" / "  Radiohead " kind of dupes.
    decomposed = unicodedata.normalize("NFKD", name)
    ascii_only = decomposed.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_only.casefold().split())


def find_near_duplicate_artists(album_artists: list[str]) -> list[list[str]]:
    """Return groups of Album Artist names that collapse to the same form.

    Surfaces case/whitespace/accent variants of the same artist so the user
    can clean them up in Music.app. Only returns groups with 2+ members.
    """
    buckets: dict[str, list[str]] = defaultdict(list)
    for name in album_artists:
        buckets[_normalise_artist_name(name)].append(name)

    return [sorted(set(names)) for names in buckets.values() if len({*names}) > 1]
