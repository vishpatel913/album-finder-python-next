import hashlib
import re
import unicodedata


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.strip().lower()).strip("-")


def slugify(name: str, extension: str | None = None) -> str:
    """Lower-case, collision-resistant id from a display name.

    A short sha1 of the original name is appended to catch similar names
    
        slugify("Made In The Manor")        -> "made-in-the-manor-9f8e7d"
        slugify("Kano", "Made In The Manor") -> "kano-made-in-the-manor-1a2b3c"
    """
    digest = hashlib.sha1(name.encode()).hexdigest()[:6]
    if extension:
        return f"{_norm(name)}-{_norm(extension)}-{digest}"
    return f"{_norm(name)}-{digest}"
