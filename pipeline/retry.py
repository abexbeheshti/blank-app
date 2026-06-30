"""Small exponential-backoff retry decorator shared by all API clients."""
from __future__ import annotations

import functools
import logging
import time
from typing import Callable, TypeVar

logger = logging.getLogger("pipeline")

T = TypeVar("T")


def with_backoff(
    *, attempts: int = 4, base_delay: float = 1.0, exceptions: tuple[type[Exception], ...] = (Exception,)
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Retry a function with exponential backoff (1s, 2s, 4s, 8s, ...).

    Used for transient API failures (rate limits, network blips). Does not
    retry on the final attempt's failure - it re-raises so callers can log
    and move on rather than crash the whole polling loop.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exc: Exception | None = None
            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:  # noqa: BLE001
                    last_exc = exc
                    if attempt == attempts - 1:
                        break
                    delay = base_delay * (2**attempt)
                    logger.warning(
                        "%s failed (attempt %d/%d): %s - retrying in %.0fs",
                        func.__name__,
                        attempt + 1,
                        attempts,
                        exc,
                        delay,
                    )
                    time.sleep(delay)
            assert last_exc is not None
            raise last_exc

        return wrapper

    return decorator
