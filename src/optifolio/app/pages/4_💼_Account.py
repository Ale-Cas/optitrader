"""Streamlit about page."""  # noqa: N999

import logging

from optifolio.app import Page, session

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main() -> None:
    """Run dashboard."""
    page = Page(name="Alpaca account dashboard")
    page.display_title_and_description(
        description="""
        Boost the portfolio analytics for your Alpaca account.
        """
    )
    session.display_alpaca_account_sidebar()
    page.display_code_sidebar()


if __name__ == "__main__":
    main()
