"""Streamlit about page."""

import logging

import streamlit as st

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main() -> None:
    """Run dashboard."""
    st.title("Backtest your strategy")
    with st.expander("Backtester description", expanded=True):
        st.markdown(
            """
        With the backtester you can see how your strategy would've performed historically.
        You just need to confirm the _start_ and _end_ dates and the backtester is going to rebalance
        your optimal portfolio based on your _rebalance frequency_ to and evaluate the performance on unseen data.
        """
        )


if __name__ == "__main__":
    main()
