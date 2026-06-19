from collections.abc import Callable, Iterable


def unique_by[T](
    items: Iterable[T],
    key: Callable[[T], object],
    merge: Callable[[T, T], T] | None = None,
) -> list[T]:
    """Collapse items sharing the same key, preserving first-seen order.

    Without `merge`: first occurrence wins.
    With `merge(existing, new)`: combine the two into the kept value.
    """
    out: dict[object, T] = {}
    for item in items:
        k = key(item)
        out[k] = merge(out[k], item) if merge and k in out else item
    return list(out.values())
