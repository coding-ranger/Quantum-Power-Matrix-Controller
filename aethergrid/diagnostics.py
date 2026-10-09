import functools
import time
import logging
from typing import Callable, Any


"""Diagnostic decorators for AetherGrid."""

logger = logging.getLogger("aethergrid.diagnostics")


def log_matrix_calculation(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator that logs function name, arguments, return value,
    execution time, and any exception raised."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Wrapped call with diagnostic logging.
            """
            start = time.perf_counter()
            logger.info(
                "Entering %s args=%s kwargs=%s",
                func.__name__,
                args,
                kwargs,
            )

            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                elapsed_ms = (time.perf_counter() - start) * 1000.0
                logger.error(
                    "Exception in %s type=%s message=%s elapsed_ms=%.3f",
                    func.__name__,
                    type(exc).__name__,
                    str(exc),
                    elapsed_ms,
                )
                raise
            else:
                elapsed_ms = (time.perf_counter() - start) * 1000.0
                logger.info(
                    "Exiting %s result=%s elapsed_ms=%.3f",
                    func.__name__,
                    result,
                    elapsed_ms,
                )
                return result

    return wrapper



