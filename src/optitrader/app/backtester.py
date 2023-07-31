"""Streamlit about page."""

import logging

from optitrader.app import Page, session

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main() -> None:
    """Run dashboard."""
    page = Page(name="Backtest your strategy")
    page.display_title_and_description(
        description="""
        The backtesting page is a user-friendly tool that allows traders and investors to assess the historical performance of their trading strategies.\n
        It offers a simple interface to check the optimization parameters and view basic metrics such as profitability and portfolio allocation over time.\n
        The dashboard presents clear visualizations, including equity curves and performance summaries, enabling users to gain insights into their strategy's effectiveness.\n
        👈 You can see the optimization problem in the _sidebar_ and the backtester is going to rebalance
        your optimal portfolio based on your _rebalance frequency_ to and evaluate the performance on unseen data. \n
        """
    )
    session.set_rebalance_frequency()
    session.run_backtest()
    session.display_backtest()
    session.display_optitrader_problem()
