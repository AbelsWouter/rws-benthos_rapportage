"""Logging decorator to check the row difference."""

"""
# File: check_decorator.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 21-01-2023
# Last modification: 20-02-2024
# Python v3.12.1
"""

import functools
import logging

import pandas as pd

from preparation import utility


# Initializing logger object to write custom logs
logger = logging.getLogger(__name__)


def row_difference_decorator(*arg_positions):
    """Logs row differences between input and output DataFrame for quality
    control and debugging.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Call the decorated function and capture its output
            result_df = func(*args, **kwargs)

            # Calculate the row difference for specified argument positions
            input_dfs = [
                args[i]
                for i in arg_positions
                if i < len(args) and isinstance(args[i], pd.DataFrame)
            ]
            input_row_count = sum(df.shape[0] for df in input_dfs)
            output_row_count = result_df.shape[0]
            actual_row_difference = input_row_count - output_row_count

            # Check if duplicate rows were removed
            if hasattr(wrapper, "records_removed") and isinstance(
                wrapper.records_removed, dict
            ):
                records_removed = wrapper.records_removed
                expected_row_difference = sum(records_removed.values())

                if abs(actual_row_difference) - expected_row_difference != 0:
                    msg = f"{func.__module__}.{func.__name__}: Onverwachte fout in het aantal records"
                    logger.critical(msg)
                    logger.error(
                        f"Input Rows: {input_row_count}, Output Rows: {output_row_count}, "
                        f"Actual Row Difference: {actual_row_difference}, "
                        f"Expected Row Difference: {expected_row_difference}"
                    )
                    utility.stop_script()
                else:
                    msg = f"{func.__module__}.{func.__name__}: Aantal records in/uit is correct"
                    logger.debug(msg)
            else:
                logger.critical(
                    "Decorator 'row_difference_decorator' is not used correctly. "
                )
                # clean attr after usage, will be remembered throughout session
                wrapper.records_removed = {}
                utility.stop_script()

            # clean attr after usage, will be remembered throughout session
            wrapper.records_removed = {}
            return result_df

        if not hasattr(wrapper, "records_removed"):
            wrapper.records_removed = {}

        return wrapper

    return decorator
