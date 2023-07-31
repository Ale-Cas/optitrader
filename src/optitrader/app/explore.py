"""Streamlit explore page."""

import logging

import plotly.express as px
import streamlit as st

from optitrader.app import Page, session
from optitrader.utils import remove_punctuation

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main() -> None:
    """Run dashboard."""
    page = Page(name="Explore financial data & news")
    page.display_title()
    asset = session.market_data.get_asset(ticker=session.ticker)
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
        asset = session.market_data.get_asset(ticker=session.ticker)
    prices = session.market_data.load_prices(
        tickers=(session.ticker,), start_date=session.start_date
    )[session.ticker]
    if not asset.name:
        log.warning(f"Asset {session.ticker} without name.")
        asset.name = session.ticker

    st.write(
        f"""
        <style>
            .container {{
                display: flex;
                align-items: center;
                margin-bottom: 20px;
            }}

            .logo {{
                border-radius: 50%;
                overflow: hidden;
            }}

            .logo img {{
                width: 50px;
                height: 50px;
            }}

            .title {{
                font-size: 30px;
                font-weight: bold;
                margin-left: 20px;
            }}
        </style>

        <div class="container">
            <div class="logo">
                <img src="{asset.logo}" alt="Logo">
            </div>
            <div class="title">{asset.name.title()}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if asset.business_summary:
        with st.expander("Business summary"):
            st.write(asset.business_summary)
    price = prices[-1]
    last_price = prices[-2]
    prev_market_cap = round(asset.number_of_shares * last_price / 1e6, 2)
    market_cap = round(asset.number_of_shares * price / 1e6, 2)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Last Day Closing Price ($)",
            value=round(price, 4),
            delta=round(price - last_price, 4),
        )
    with col2:
        st.metric(
            label="Market Capitalization (Mln $)",
            value=market_cap,
            delta=round(market_cap - prev_market_cap, 2),
        )
    with col3:
        st.metric(label="Main Exchange", value=asset.exchange.value)
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
        st.header(remove_punctuation(asset.name.split()[0]).split()[0].title())
        st.dataframe(
            asset.to_series(),
            use_container_width=True,
            height=400,
        )
    session.display_news()
