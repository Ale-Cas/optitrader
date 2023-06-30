"""Streamlit base page component."""
import streamlit as st

from optifolio.app.session_manager import SessionManager


class Page:
    """Page class."""

    def __init__(self, name: str, session: SessionManager) -> None:
        self.name = name
        self.session = session

    def display_title_and_description(self, description: str) -> None:
        """Display title and description."""
        st.title(self.name.title())
        with st.expander("Description", expanded=True):
            st.markdown(description)
