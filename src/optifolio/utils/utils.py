"""General utils."""


def clean_string(string: str) -> str:
    """Clean up a string and return the cleaned string."""
    return string.replace("_", " ").replace("-", " ")
