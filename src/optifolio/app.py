"""Streamlit app."""

import logging

import pandas as pd
import plotly.express as px
import streamlit as st

from optifolio import Optifolio
from optifolio.backtester import Backtester, Portfolios, RebalanceFrequency
from optifolio.market.investment_universe import InvestmentUniverse, UniverseName
from optifolio.optimization.objectives import ObjectiveName, objective_mapping

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

st.set_page_config(
    page_title="Optifolio",
    page_icon="🛠️",
    layout="wide",
)
st.title("Optifolio Dashboard")

universe_name = st.selectbox(
    label="Choose the investment universe.",
    options=[name.value for name in list(UniverseName)],
)
objective_names = st.multiselect(
    label="Choose one or more objective functions for your optimal portfolio.",
    options=[obj_name.value for obj_name in list(ObjectiveName)],
    default=[ObjectiveName.CVAR],
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
    st.header("Optimal portfolio settings:")
    universe_name = UniverseName(universe_name) if universe_name else UniverseName.FAANG
    num_assets = None
    min_num_assets = None
    max_num_assets = None
    min_weight = None
    max_weight = None
    _num = st.checkbox("Choose exact number of assets you want in your portfolio.")
    _min_num = st.checkbox("Choose minimum number of assets you want in your portfolio.")
    _max_num = st.checkbox("Choose maximum number of assets you want in your portfolio.")
    _min_max = _min_num or _max_num
    if _num and not _min_max:
        num_assets = st.number_input(
            label="Exact number of assets.",
            value=3,
            min_value=1,
            step=1,
            max_value=len(InvestmentUniverse(name=universe_name).tickers),
        )
    elif _min_max and not _num:
        if _min_num:
            min_num_assets = st.number_input(
                label="Minimum number of assets.",
                value=2,
                min_value=1,
                step=1,
                max_value=len(InvestmentUniverse(name=universe_name).tickers),
            )
        if _max_num:
            max_num_assets = st.number_input(
                label="Maximum number of assets.",
                value=4,
                min_value=2,
                step=1,
                max_value=len(InvestmentUniverse(name=universe_name).tickers),
            )
    elif _min_max and _num:
        st.error("You can only provide the exact number of assets or the bounds!")
    if st.checkbox(
        "Choose minimum weight in percentage for each asset in the investment universe."
    ):
        min_weight = st.number_input(
            label="Minimum weight percentage.",
            value=1,
            min_value=1,
            step=1,
            max_value=int(100 / len(InvestmentUniverse(name=universe_name).tickers)),
        )
    if st.checkbox(
        "Choose the maximum weight in percentage that you want an asset in your portfolio to have."
    ):
        max_weight = st.number_input(
            label="Maximum weight percentage.",
            value=40,
            min_value=10,
            step=1,
            max_value=100,
        )

if objective_names and universe_name:
    opt = Optifolio(
        objectives=[objective_mapping[ObjectiveName(o)] for o in objective_names],
        universe_name=UniverseName(universe_name),
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
                    num_assets=int(num_assets) if num_assets else None,
                    min_num_assets=int(min_num_assets) if min_num_assets else None,
                    max_num_assets=int(max_num_assets) if max_num_assets else None,
                    min_weight_pct=int(min_weight) if min_weight else None,
                    max_weight_pct=int(max_weight) if max_weight else None,
                )
            except AssertionError as er:
                log.warning(er)
                st.error("Couldn't find a solution!")
        with st.spinner("Elaborating solution"):
            weights = opt_ptf.get_non_zero_weights()

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
