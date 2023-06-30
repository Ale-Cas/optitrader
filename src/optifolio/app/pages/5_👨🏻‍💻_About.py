"""Streamlit about page."""  # noqa: N999

import logging

from optifolio.app import Page

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main() -> None:
    """Run dashboard."""
    page = Page(name="About optifolio")
    page.display_title_and_description(
        description="""
        Optifolio is an open-source Python repository for portfolio optimization and quantitative finance.
        """
    )
    page.display_code_sidebar(with_divider=False)


if __name__ == "__main__":
    main()
