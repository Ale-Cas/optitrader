"""Streamlit session manager."""
from decimal import Decimal
from enum import Enum
from numbers import Number
from typing import Any

import streamlit as st
from streamlit.runtime.state import SessionStateProxy
from typeguard import typechecked

from optifolio.enums.iterable import IterEnum


class SessionManager:
    """Streamlit session manager."""

    def __init__(self) -> None:
        self.state: SessionStateProxy = st.session_state
        self.market_data = None

    def get(self, field: Any) -> Any:
        """Get from the session state."""
        return self.state[f"{field}"]

    def typed_get(self, field: Any) -> Any:
        """Get from the session state."""
        value = self.get(field)
        assert isinstance(value, type(field))
        if isinstance(value, str):
            return self.get_string(field)
        if isinstance(value, Number):
            return self.get_number(field)
        if isinstance(value, Enum):
            return self.get_enum(field)
        return value

    @typechecked
    def get_string(self, string: str) -> str:
        """Get a string on the session state."""
        return self.get(string)

    @typechecked
    def get_number(self, number: str) -> str:
        """Get a number on the session state."""
        return self.get(number)

    @typechecked
    def get_enum(self, field: Enum) -> Enum:
        """Get on the session_state."""
        return self.get(field)

    def write(self, field: Any) -> Any:
        """Write on the session_state."""
        self.state[f"{field}"] = field
        return self.get(field)

    @typechecked
    def write_enum(self, field: Enum) -> Enum:
        """Write on the session_state."""
        self.state[f"{field.name}"] = field.value
        return self.get(field)

    @typechecked
    def write_string(self, string: str) -> str:
        """Write a string on the session state."""
        return self.write(string)

    @typechecked
    def write_number(self, number: int | float | Decimal) -> int | float | Decimal:
        """Write a number on the session state."""
        return self.write(number)

    def delete(self, field: Any) -> None:
        """Delete from the session state."""
        self.state[f"{field}"] = None
        assert self.get(field) is None, f"Session state had {self.get(field)}"

    def write_from_selectbox(self, label: str, options: type[IterEnum]) -> str:
        """Write a string from the selectbox."""
        selected = st.selectbox(
            label=label,
            options=options.get_values_list(),
            index=0,
        )
        if selected:
            self.write_string(selected)
            return self.get_string(selected)
        raise AssertionError("Couldn't write to cache.")

    def write_from_multiselect(
        self, label: str, options: type[IterEnum], default: bool = True
    ) -> list[str]:
        """Write a string from the multiselect."""
        _opts = options.get_values_list()
        selected = st.multiselect(
            label=label, options=_opts, default=[_opts[0]] if default else None
        )
        for item in selected:
            assert isinstance(item, str)
            self.write_string(item)
        return selected


session = SessionManager()
