"""Streamlit app."""

from importlib.metadata import version

import streamlit as st

st.title(f"optifolio v{version('optifolio')}")  # type: ignore[no-untyped-call]
