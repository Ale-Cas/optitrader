"""General utils."""
import re

import pandas as pd


def remove_punctuation(string: str) -> str:
    """Remove punctuation marks in a string."""
    return re.sub(r"[^\w\s]", "", string.replace(".", " "))


def clean_string(string: str) -> str:
    """Clean up a string and return the cleaned string."""
    return string.replace("_", " ").replace("-", " ")


def rearrange_columns_by_zeros(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rearranges the columns of a DataFrame based on the number of zeros in each column.

    Parameters
    ----------
    `df`: (DataFrame) The input DataFrame.

    Returns
    -------
    `DataFrame`: The rearranged DataFrame.
    """
    # Count the number of zeros in each column
    zeros_count = df.eq(0).sum()

    # Sort the columns based on the number of zeros in ascending order
    sorted_columns = zeros_count.sort_values().index

    # Rearrange the columns in the dataframe
    return df[sorted_columns]
