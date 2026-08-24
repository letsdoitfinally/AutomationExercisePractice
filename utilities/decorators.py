import logging
import time
from functools import wraps
from typing import Callable, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable)


def logging_decorator(func: F) -> F:
    """Log method execution and failures.

    Args:
        func: Function to decorate.

    Returns:
        The decorated function.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(
            "Executing %s",
            func.__qualname__,
        )

        try:
            result = func(*args, **kwargs)

            logger.debug(
                "Successfully executed %s",
                func.__qualname__,
            )

            return result

        except Exception:
            logger.exception(
                "Exception occurred while executing %s",
                func.__qualname__,
            )
            raise

    return wrapper


def retry_on_exception(
    times: int = 3,
    exception_type: type[Exception] = Exception,
    delay: float = 0,
) -> Callable:
    """Retry a function when a specified exception occurs.

    Args:
        times: Maximum number of attempts.
        exception_type: Exception type that should trigger a retry.
        delay: Delay in seconds between retry attempts.

    Returns:
        A decorator that retries the decorated function.

    Raises:
        ValueError: If ``times`` is less than one.
    """
    if times < 1:
        raise ValueError("times must be at least 1.")

    def decorator(func: F) -> F:

        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)

                except exception_type:
                    if attempt == times:
                        logger.exception(
                            "%s failed after %s attempts.",
                            func.__qualname__,
                            times,
                        )
                        raise

                    logger.warning(
                        "%s failed on attempt %s/%s. Retrying...",
                        func.__qualname__,
                        attempt,
                        times,
                    )

                    if delay:
                        time.sleep(delay)

        return wrapper

    return decorator