"""Streamlit about page."""

import logging

import streamlit as st

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main() -> None:
    """Run dashboard."""
    st.title("Explore financial news and information")


if __name__ == "__main__":
    main()
