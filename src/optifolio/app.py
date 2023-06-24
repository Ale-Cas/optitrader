"""Streamlit app."""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from optifolio.market.market_data import MarketData
from optifolio.optimization.constraints import NoShortSellConstraint, SumToOneConstraint
from optifolio.optimization.objectives import ObjectiveName, objective_mapping
from optifolio.optimization.solver import Solver

st.title("Optifolio Dashboard")

objective_names = st.multiselect(
    label="Choose objectives", options=[obj_name.value for obj_name in list(ObjectiveName)]
)
start_date = st.date_input(
    label="Choose the start date.",
    value=pd.Timestamp.today() - pd.Timedelta(value=365 * 2, unit="day"),
)
TEST_TICKERS = (
    "AAPL",
    "AMZN",
    "TSLA",
    "GOOGL",
    "BRK.B",
    "V",
    "JPM",
    "NVDA",
    "MSFT",
    "DIS",
    "NFLX",
    "META",
    "WMT",
    "BABA",
    "AMD",
    "ACN",
    "PFE",
    "ORCL",
    "ZM",
    "SHOP",
    "COIN",
)
if objective_names:
    market_data = MarketData()
    solver = Solver(
        returns=market_data.get_total_returns(
            tickers=TEST_TICKERS,
            start_date=pd.Timestamp(start_date),
            end_date=pd.Timestamp.today().utcnow() - pd.Timedelta(value=1, unit="day"),
        ),
        objective_functions=[
            objective_mapping[ObjectiveName(obj_name)] for obj_name in objective_names
        ],
        constraint_functions=[SumToOneConstraint(), NoShortSellConstraint()],
    )
    if st.button(label="Solve optimization problem."):
        opt_ptf = solver.solve(weights_tolerance=1e-2)
        fig1, ax1 = plt.subplots()
        weights = opt_ptf.get_non_zero_weights()
        ax1.pie(
            weights.values,
            labels=weights.keys(),
            autopct="%1.1f%%",
            # shadow=True,
            startangle=90,
        )
        ax1.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.

        st.pyplot(fig1)
        opt_ptf.set_market_data(market_data)
        st.dataframe(opt_ptf.get_holdings_df())
