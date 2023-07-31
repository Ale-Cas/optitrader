"""Streamlit base page component."""
import streamlit as st


class Page:
    """Page class."""

    def __init__(
        self,
        name: str,
    ) -> None:
        self.name = name
        st.set_page_config(
            page_title="optitrader",
            page_icon="🛠️",
            layout="wide",
        )

    def display_title(self) -> None:
        """Display title."""
        st.title(self.name.title())

    def display_title_and_description(self, description: str) -> None:
        """Display title and description."""
        self.display_title()
        with st.expander("Description", expanded=True):
            st.markdown(description)

    @staticmethod
    def display_code_sidebar(with_divider: bool = True) -> None:
        """Display github link to code in sidebar."""
        with st.sidebar:
            if with_divider:
                st.divider()
            st.header("💻 Code")
            st.code("pip install optitrader")
            st.markdown(
                "[![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/Ale-Cas/optitrader)"
            )
