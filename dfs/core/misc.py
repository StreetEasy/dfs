import logging
from typing import Callable, List


from .exceptions import DataFrameValidationError


logger = logging.getLogger(__name__)


class StateBorg:
    """using Borg pattern to share state between instances"""

    __shared_state: dict = {"errors": [], "summary": True}

    def __init__(self, summary: bool = True):
        self.__dict__ = self.__shared_state
        self.__shared_state["summary"] = summary

    @property
    def errors(self) -> List[Exception]:
        return self.__shared_state["errors"]

    def set_mode(self, summary: bool):
        logger.debug(f"Setting summary={summary}")
        self.__shared_state["summary"] = summary

    @property
    def summary_error_text(self) -> str:
        return "\n".join([f"- {e.args[0]}" for e in self.__shared_state["errors"]])

    def flush_errors(self):
        self.__shared_state["errors"] = []
        logger.debug("Errors flushed")

    def handle_error(self, error: Exception):
        """if mode is summary, adds error to list of errors,
        to be raised together.

            if mode is fast, raises error immediately.
        """
        if self.__shared_state["summary"]:
            logger.debug(f"Error added: {error}")
            self.__shared_state["errors"].append(error)
        else:
            raise error


STATE = StateBorg(summary=True)


def exception_collector(func: Callable) -> Callable:
    """Decorator that collects exceptions and returns the summary"""

    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except DataFrameValidationError as e:
            STATE.handle_error(e)
            return None

    return inner_function
