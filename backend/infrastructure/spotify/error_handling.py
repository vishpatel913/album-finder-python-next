import functools
import logging
from collections.abc import Callable

from pydantic import ValidationError

logger = logging.getLogger(__name__)


def log_validation_error(error: ValidationError, context: str) -> None:
    for err in error.errors():
        field_path = ".".join(str(p) for p in err["loc"]) or "<root>"
        logger.warning(
            "%s — validation failed on '%s': %s (got: %r)",
            context,
            field_path,
            err["msg"],
            err["input"],
        )


def handle_validation_errors[**P, T](func: Callable[P, T]) -> Callable[P, T | None]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            log_validation_error(e, context=func.__qualname__)
            return None

    return wrapper
