"""Streamlit about page."""  # noqa: N999

import logging

from optifolio.app import Page, session

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main() -> None:
    """Run dashboard."""
    page = Page(name="Backtest your strategy")
    page.display_title_and_description(
        description="""
        With the backtester you can see how your strategy would've performed historically.\n
        👈 You can see the optimization problem in the _sidebar_ and the backtester is going to rebalance
        your optimal portfolio based on your _rebalance frequency_ to and evaluate the performance on unseen data. \n
        """
    )
    session.set_rebalance_frquency()
    session.run_backtest()
    session.display_optifolio_problem()


if __name__ == "__main__":
    main()
