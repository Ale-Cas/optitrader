"""Streamlit app."""

import pandas as pd
import plotly.express as px
import streamlit as st

from optifolio.investment_universe import TEST_TICKERS
from optifolio.market.market_data import MarketData
from optifolio.optimization.constraints import NoShortSellConstraint, SumToOneConstraint
from optifolio.optimization.objectives import ObjectiveName, objective_mapping
from optifolio.optimization.solver import Solver

st.title("Optifolio Dashboard")

objective_names = st.multiselect(
    label="Choose objectives", options=[obj_name.value for obj_name in list(ObjectiveName)]
)
start_date = pd.Timestamp(
    st.date_input(
        label="Choose the start date.",
        value=pd.Timestamp.today() - pd.Timedelta(value=365 * 2, unit="day"),
    )
)

if objective_names:
    market_data = MarketData()
    solver = Solver(
        returns=market_data.get_total_returns(
            tickers=TEST_TICKERS,
            start_date=start_date,
            end_date=pd.Timestamp.today().utcnow() - pd.Timedelta(value=1, unit="day"),
        ),
        objectives=[objective_mapping[ObjectiveName(obj_name)] for obj_name in objective_names],
        constraints=[SumToOneConstraint(), NoShortSellConstraint()],
    )
    if st.button(label="Solve optimization problem."):
        opt_ptf = solver.solve(weights_tolerance=1e-2)
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
        st.dataframe(opt_ptf.get_holdings_df())
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
