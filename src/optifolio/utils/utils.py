"""General utils."""
import re


def remove_punctuation(string: str) -> str:
    """Remove punctuation marks in a string."""
    return re.sub(r"[^\w\s]", "", string)


def clean_string(string: str) -> str:
    """Clean up a string and return the cleaned string."""
    return string.replace("_", " ").replace("-", " ")
