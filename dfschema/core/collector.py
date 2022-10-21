from typing import Callable
from .exceptions import DataFrameValidationError


def exception_collector(func: Callable) -> Callable:
    """Decorator that collects exceptions and returns the summary"""

    def inner_function(*args, root, **kwargs) -> None:
        """
        root: DfSchema object, assumed to have `_summary`, `_exception_pool` attributes
        """
        try:
            func(*args, **kwargs)
        except DataFrameValidationError as e:
            # STATE.handle_error(e)
            if root._summary:
                root._exception_pool.append(e)
            else:
                raise DataFrameValidationError(e)

            return None
        except TypeError as e:  # Note: for debugging
            raise TypeError(func, e)

    return inner_function
