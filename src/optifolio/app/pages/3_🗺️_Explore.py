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
    opt = session.get_optifolio()
    with st.form(key="search"):
        col1, col2 = st.columns(2)
        with col1:
            _ = st.text_input("Search for a stock by name", placeholder="Apple")
        with col2:
            ticker = st.text_input("Search by ticker", placeholder="AAPL") or default_ticker

        st.write("Your universe tickers")
        tickers = sorted(opt.investment_universe.tickers)
        tickers_per_row = 10
        len_tickers = len(tickers)
        if len_tickers > tickers_per_row:
            for i in range(0, len_tickers, tickers_per_row):
                row = tickers[i : i + tickers_per_row]
                cols = st.columns(tickers_per_row)
                for idx, col in enumerate(cols):
                    with col:
                        if idx < len(row):
                            st.code(row[idx])
        else:
            cols = st.columns(len(tickers))
            for idx, col in enumerate(cols):
                with col:
                    st.code(tickers[idx])
        st.form_submit_button("SEARCH")
    market_data = MarketData()
    asset = market_data.get_asset_from_ticker(ticker=ticker)
    prices = market_data.load_prices(tickers=(ticker,), start_date=session.start_date)[ticker]
    st.header(asset.name)
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
    with st.sidebar:
        st.subheader(f"{asset.name.split()[0]} key facts")
        st.dataframe(
            asset.to_series(),
            use_container_width=True,
            height=400,
        )


if __name__ == "__main__":
    main()
