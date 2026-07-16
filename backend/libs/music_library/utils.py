import re

_FEATURED_RE = re.compile(
    r"[\(\[]\s*(?:featuring|feat\.?|ft\.?)\s+(?P<artists>[^)\]]+?)\s*[\)\]]",
    re.IGNORECASE,
)
_FEATURED_SPLIT_RE = re.compile(r"\s*(?:,|&|\band\b)\s*", re.IGNORECASE)


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
