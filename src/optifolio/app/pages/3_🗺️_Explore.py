"""Streamlit about page."""  # noqa: N999

import logging

import plotly.express as px
import streamlit as st

from optifolio.app import Page, session
from optifolio.market import MarketData

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main() -> None:
    """Run dashboard."""
    page = Page(name="Explore financial data and news")
    page.display_title()
    default_ticker = "AAPL"
    with st.form(key="search"):
        st.text_input("Search for a stock by name", placeholder="Apple")
        ticker = st.text_input("Search by ticker", placeholder="AAPL") or default_ticker
        st.form_submit_button()
    market_data = MarketData()
    asset = market_data.get_asset_from_ticker(ticker=ticker)
    prices = market_data.load_prices(tickers=(ticker,), start_date=session.start_date)[ticker]
    st.header(asset.name)
    with st.expander("Business summary"):
        st.write(asset.business_summary)
    st.write("Market Capitalization")
    st.subheader(f"{round(asset.total_number_of_shares * prices[-1] / 1e6)!s} Mln $")
    st.plotly_chart(
        px.line(
            data_frame=prices,
            x=prices.index,
            y=prices.values,
            labels={"timestamp": "", "y": ""},
            title="Close prices",
        ),
        use_container_width=True,
    )
    with st.sidebar:
        st.subheader(f"{asset.name.split()[0]} key facts")
        st.dataframe(
            asset.to_series(),
            use_container_width=True,
            height=500,
            column_config={
                "Weight In Ptf": None,
            },
        )


if __name__ == "__main__":
    main()
