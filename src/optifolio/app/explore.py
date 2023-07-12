"""Streamlit explore page."""

import logging

import plotly.express as px
import streamlit as st

from optifolio.app import Page, session
from optifolio.utils import remove_punctuation

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main() -> None:
    """Run dashboard."""
    page = Page(name="Explore financial data & news")
    page.display_title()
    asset = session.market_data.get_asset_from_ticker(ticker=session.ticker)
    submitted = False
    with st.form(key="search"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Search for a stock by name", placeholder=asset.name)
            if name:
                session.set_ticker(session.market_data.get_asset_by_name(name).symbol)
        with col2:
            ticker = st.text_input("Search by ticker", placeholder=session.ticker)
            if ticker:
                session.set_ticker(ticker)

        session.display_tickers()
        submitted = st.form_submit_button("SEARCH 🔍", help="Search for a stock by ticker or name.")
    if submitted:
        asset = session.market_data.get_asset_from_ticker(ticker=session.ticker)
    prices = session.market_data.load_prices(
        tickers=(session.ticker,), start_date=session.start_date
    )[session.ticker]
    st.header(asset.name.title())
    with st.expander("Business summary"):
        st.write(asset.business_summary)
    last_price = prices[-1]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            #### Last Day Closing Price\n
            ### :green[{round(last_price, 2)!s} $]
            """
        )
    with col2:
        st.markdown(
            f"""
            #### Market Capitalization\n
            ### :green[{round(asset.number_of_shares * last_price/ 1e6, 2)!s} Mln $]
            """
        )
    with col3:
        st.markdown(
            f"""
            #### Main Exchange\n
            ### :red[{asset.exchange}]
            """
        )
    st.plotly_chart(
        px.line(
            data_frame=prices,
            x=prices.index,
            y=prices.values,
            labels={"timestamp": "", "y": ""},
            title="Historical end of day closing prices",
        ),
        use_container_width=True,
    )
    session.display_financials()
    with st.sidebar:
        st.subheader(f"{remove_punctuation(asset.name.split()[0]).title()} key facts")
        st.dataframe(
            asset.to_series(),
            use_container_width=True,
            height=400,
        )
    session.display_news()
