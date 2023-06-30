"""Streamlit homepage."""  # noqa: N999
import logging

import pandas as pd
import plotly.express as px
import streamlit as st

from optifolio import Optifolio
from optifolio.app.page import Page
from optifolio.app.session_manager import session
from optifolio.backtester import Backtester, Portfolios, RebalanceFrequency
from optifolio.enums import ObjectiveName
from optifolio.market.investment_universe import UniverseName
from optifolio.market.market_data import MarketData
from optifolio.optimization.objectives import objective_mapping

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main() -> None:  # noqa: PLR0915
    """Run dashboard."""
    st.set_page_config(
        page_title="Optifolio",
        page_icon="🛠️",
        layout="wide",
    )
    page = Page(name="Optifolio dashboard", session=session)
    page.display_title_and_description(
        description="""
        In this dashboard you can configure your optimal portfolio using several parameters.
        You can select the stocks that the solver should take into consideration when choosing the _investment universe_,
        then you can add and configure _objectives_ and _constraints_ for the optimization problem.
        Once you compute the optimal portfolio, analyze the solution obtained and
        head to the _backtester_ page to see how your strategy would've performed historically.
        """
    )

    universe_name = session.write_from_selectbox(
        label="Choose the investment universe.",
        options=UniverseName,
    )
    objective_names = session.write_from_multiselect(
        label="Choose one or more objective functions for your optimal portfolio.",
        options=ObjectiveName,
    )
    with st.expander("Objectives configuration."):
        for obj in objective_names:
            st.number_input(
                f"Enter {obj} weight",
                min_value=0.1,
                max_value=1.0,
                step=0.1,
                value=0.5,
            )
    start_date = pd.Timestamp(
        st.date_input(
            label="Choose the first date used to retrieve prices for the optimization.",
            value=pd.Timestamp.today() - pd.Timedelta(value=365 * 2, unit="day"),
        )
    )
    rebal_freq = st.selectbox(
        label="Choose the rebalance frequency.",
        options=[freq.name.title() for freq in list(RebalanceFrequency)],
        index=2,
    )

    with st.sidebar:
        st.header("🦙 Alpaca Account")
        st.write("The default data come from my personal Alpaca trading sandbox API keys.")
        st.markdown(
            """
            [You can find your api keys here](https://alpaca.markets/docs/trading/getting_started/#creating-an-alpaca-account-and-finding-your-api-keys)
            and enter them below to use your account 👇"""
        )
        with st.form(key="api-keys"):
            api_key = session.write_string(st.text_input("Enter your Alpaca Trading API key"))
            secret_key = session.write_string(st.text_input("Enter your Alpaca Trading API secret"))
            keys_submitted = st.form_submit_button("Login")
        st.divider()
        st.header(" Code")
        st.code("pip install optifolio")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                "[![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/AvratanuBiswas/PubLit)"
            )
        with col2:
            st.markdown("👨🏻‍💻 _Alessio Castrica_")

    if objective_names and universe_name:
        market_data = None
        if keys_submitted and secret_key and api_key:
            market_data = MarketData(trading_key=api_key, trading_secret=secret_key)
        opt = Optifolio(
            objectives=[objective_mapping[ObjectiveName(o)] for o in objective_names],
            universe_name=UniverseName(universe_name),
            market_data=market_data,
        )
        col1, col2 = st.columns(2)
        with col1:
            solve_button = st.button(label="COMPUTE OPTIMAL PORTFOLIO")
        with col2:
            backtest_button = st.button(label="BACKTEST STRATEGY")
        if solve_button:
            with st.spinner("Optimization in progress"):
                try:
                    opt_ptf = opt.solve(
                        start_date=start_date,
                        weights_tolerance=1e-3,
                    )
                except AssertionError as er:
                    log.warning(er)
                    st.error("Couldn't find a solution!")
            with st.spinner("Elaborating solution"):
                st.plotly_chart(
                    figure_or_data=opt_ptf.pie_plot(),
                    use_container_width=True,
                )
                opt_ptf.set_market_data(opt.market_data)
                _cols = ["name", "weight_in_ptf"]
                holdings_df = opt_ptf.get_holdings_df()
                st.dataframe(
                    holdings_df,
                    column_order=[*_cols, *(c for c in holdings_df.columns if c not in _cols)],
                )
                st.plotly_chart(
                    figure_or_data=opt_ptf.history_plot(start_date=start_date),
                    use_container_width=True,
                )
        if backtest_button:
            with st.spinner("Backtest in progress"):
                backtester = Backtester(
                    opt=opt,
                    start=start_date,
                    rebal_freq=RebalanceFrequency[rebal_freq.upper()]
                    if rebal_freq
                    else RebalanceFrequency.MONTHLY,
                )
                ptfs = backtester.compute_portfolios()
                backtest_history = backtester.compute_history_values()
                st.plotly_chart(
                    figure_or_data=px.line(
                        data_frame=backtest_history,
                        x=backtest_history.index,
                        y=backtest_history.values,
                        labels={"timestamp": "", "y": ""},
                        title="Portfolio value from start date to today",
                    ),
                    use_container_width=True,
                )
                st.dataframe(Portfolios(ptfs).to_df().sort_index(ascending=False))


if __name__ == "__main__":
    main()
