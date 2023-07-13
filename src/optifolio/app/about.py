"""Streamlit about page."""

from optifolio.app import Page


def main() -> None:
    """Run dashboard."""
    page = Page(name="About optifolio")
    page.display_title_and_description(
        description="""
        Optifolio is an open-source Python repository for portfolio optimization and quantitative finance.
        """
    )
    page.display_code_sidebar(with_divider=False)
