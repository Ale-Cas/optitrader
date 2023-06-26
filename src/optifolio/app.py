"""Streamlit app."""

import pandas as pd
import plotly.express as px
import streamlit as st

from optifolio.market.investment_universe import InvestmentUniverse, UniverseName
from optifolio.market.market_data import MarketData
from optifolio.optimization.constraints import NoShortSellConstraint, SumToOneConstraint
from optifolio.optimization.objectives import ObjectiveName, objective_mapping
from optifolio.optimization.solver import Solver

st.title("Optifolio Dashboard")

universe_name = st.selectbox(
    label="Choose the investment universe",
    options=[name.value for name in list(UniverseName)],
)
objective_names = st.multiselect(
    label="Choose objectives",
    options=[obj_name.value for obj_name in list(ObjectiveName)],
    default=[ObjectiveName.CVAR],
)
start_date = pd.Timestamp(
    st.date_input(
        label="Choose the start date.",
        value=pd.Timestamp.today() - pd.Timedelta(value=365 * 2, unit="day"),
    )
)

if objective_names and universe_name:
    market_data = MarketData()
    solver = Solver(
        returns=market_data.get_total_returns(
            tickers=InvestmentUniverse(name=UniverseName(universe_name)).tickers,
            start_date=start_date,
            end_date=pd.Timestamp.today().utcnow() - pd.Timedelta(value=1, unit="day"),
        ),
        objectives=[objective_mapping[ObjectiveName(obj_name)] for obj_name in objective_names],
        constraints=[SumToOneConstraint(), NoShortSellConstraint()],
    )
    if st.button(label="Solve optimization problem."):
        with st.spinner("Optimization in progress"):
            opt_ptf = solver.solve(weights_tolerance=1e-2)
        with st.spinner("Elaborating solution"):
            weights = opt_ptf.get_non_zero_weights()

            st.plotly_chart(
                figure_or_data=px.pie(
                    data_frame=weights,
                    names=weights.keys(),
                    values=weights.values,
                    title="Portfolio Allocation",
                ),
                use_container_width=True,
            )
            opt_ptf.set_market_data(market_data)
            _cols = ["name", "weight_in_ptf"]
            holdings_df = opt_ptf.get_holdings_df()
            st.dataframe(
                holdings_df,
                column_order=[*_cols, *(c for c in holdings_df.columns if c not in _cols)],
            )
            history = opt_ptf.get_history(start_date=start_date)
            st.plotly_chart(
                figure_or_data=px.line(
                    data_frame=history,
                    x=history.index,
                    y=history.values,
                    # labels={"timestamp": "Days", "y": "Portfolio Value"},
                    labels={"timestamp": "", "y": ""},
                    title="Portfolio Value",
                ),
                use_container_width=True,
            )
