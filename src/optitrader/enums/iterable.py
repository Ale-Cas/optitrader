"""Iterable enumerations."""

from enum import Enum


class IterEnum(str, Enum):
    """An iterable enumeration of string."""

    @classmethod
    def get_values_list(cls) -> list[str]:
        """Get the values in a list."""
        return [member.value for member in cls]

    @classmethod
    def get_names_list(cls) -> list[str]:
        """Get the names in a list."""
        return [member.name for member in cls]

    @classmethod
    def get_index_of_value(cls, value: str) -> int:
        """Get the index of the value in the values list."""
        try:
            return cls.get_values_list().index(value)
        except ValueError as ve:
            raise ValueError(f"Value not found in the Enum {cls.__name__}") from ve
