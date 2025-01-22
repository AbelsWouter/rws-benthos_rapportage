"""Decorator to log information about functions calls and their arguments."""

"""
# File: log_decorator.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 21-05-2023
# Last modification: 20-02-2024
# Python v3.12.1
"""

import functools
import logging
import typing

import pandas as pd


def log_factory(filename: str) -> typing.Any:
    """Logs information about function calls and their return values.

    Args:
        filename (str): The logfile name

    Raises:
        e: Exception

    Returns:
        log: the log message to be written in the logfile.
    """
    logger = logging.getLogger(filename)

    def log(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            if signature:
                if isinstance(signature, pd.DataFrame):
                    logger.debug(
                        f"{func.__name__} called with args \n {signature.count()}"
                    )
                else:
                    logger.debug(f"{func.__name__} called with args \n {signature}")
            else:
                logger.debug(f"{func.__name__} called")

            try:
                result = func(*args, **kwargs)
                if isinstance(result, pd.DataFrame):
                    logger.debug(
                        f"function {func.__name__} returns \n {result.count()}"
                    )
                else:
                    logger.debug(f"function {func.__name__} returns {result}")

                return result
            except Exception as e:
                logger.exception(
                    f"Exception raised in {func.__name__}. exception: {str(e)}"
                )
                raise e

        return wrapper

    return log
