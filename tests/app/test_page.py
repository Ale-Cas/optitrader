"""Test page module."""

from unittest.mock import MagicMock, Mock

import pytest
import streamlit as st

from optitrader.app.page import Page


@pytest.fixture
def page():
    """Test page."""
    return Page(name="Test Page")


def test_display_title(page: Page):
    """Test for the display_title method of Page class."""
    st.title = Mock()

    page.display_title()

    st.title.assert_called_once_with("Test Page")


def test_display_title_and_description(page: Page):
    """Test for the display_title_and_description method of Page class."""
    st.title = Mock()
    st.expander = MagicMock()
    st.markdown = Mock()

    page.display_title_and_description("Test Description")

    st.title.assert_called_once_with("Test Page")
    st.expander.assert_called_once_with("Description", expanded=True)
    st.markdown.assert_called_once_with("Test Description")


def test_display_code_sidebar(page: Page):
    """Test for the display_code_sidebar method of Page class."""
    st.sidebar = MagicMock()
    st.divider = Mock()
    st.header = Mock()
    st.code = Mock()
    st.markdown = Mock()

    page.display_code_sidebar(with_divider=True)

    assert len(st.sidebar.mock_calls) == 2  # noqa: PLR2004 # enter and exit
    st.divider.assert_called_once()
    st.header.assert_called_once_with("💻 Code")
    st.code.assert_called_once_with("pip install optitrader")
    st.markdown.assert_called_once_with(
        "[![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/Ale-Cas/optitrader)"
    )


# TODO: Add more test cases for other methods as needed
