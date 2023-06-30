"""Streamlit session manager."""

import logging

import pandas as pd
import plotly.express as px
import streamlit as st

from optifolio.backtester import Backtester, Portfolios
from optifolio.enums import (
    ConstraintName,
    IterEnum,
    ObjectiveName,
    RebalanceFrequency,
    UniverseName,
)
from optifolio.main import Optifolio
from optifolio.market import MarketData
from optifolio.optimization.objectives import objective_mapping

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class SessionManager:
    """Streamlit session manager."""

    def __init__(self) -> None:
        self.market_data: MarketData | None = None
        self.universe_name = UniverseName.FAANG
        self.objective_names = [ObjectiveName.CVAR]
        self.constraint_names = [ConstraintName.SUM_TO_ONE, ConstraintName.LONG_ONLY]
        self.start_date = pd.Timestamp.today() - pd.Timedelta(value=365 * 2, unit="day")
        self.rebalance_frequency = RebalanceFrequency.MONTHLY

    def _from_selectbox(self, label: str, options: type[IterEnum], is_value: bool = True) -> str:
        """Return the selected value from the selectbox."""
        sel = st.selectbox(
            label=label,
            options=options.get_values_list() if is_value else options.get_names_list(),
            index=0,
        )
        return sel or ""

    def _from_multiselect(
        self, label: str, options: type[IterEnum], default: bool = True
    ) -> list[str]:
        """Return a list from the multiselect."""
        _opts = options.get_values_list()
        return st.multiselect(label=label, options=_opts, default=[_opts[0]] if default else None)

    def set_api_keys(self) -> None:
        """Set the API keys."""
        with st.form(key="api-keys"):
            api_key = st.text_input("Enter your Alpaca Trading API key")
            secret_key = st.text_input("Enter your Alpaca Trading API secret")
            keys_submitted = st.form_submit_button("Login")
        if api_key and secret_key and keys_submitted:
            self.market_data = MarketData(
                trading_key=api_key,
                trading_secret=secret_key,
            )

    def set_universe_name(self) -> None:
        """Set the universe name."""
        self.universe_name = UniverseName(
            self._from_selectbox(
                label="Choose the investment universe.",
                options=UniverseName,
            )
        )

    def set_start_date(self) -> None:
        """Set the optimization start_date."""
        self.start_date = pd.Timestamp(
            st.date_input(
                label="Choose the first date used to retrieve prices for the optimization.",
                value=self.start_date,
            )
        )

    def set_objective_names(self) -> None:
        """Set the objectives name."""
        self.objective_names = [
            ObjectiveName(o)
            for o in self._from_multiselect(
                label="Choose one or more objective functions for your optimal portfolio.",
                options=ObjectiveName,
            )
        ]

    def set_constraint_names(self) -> None:
        """Set the constraints name."""
        self.constraint_names = [
            ConstraintName(o)
            for o in self._from_multiselect(
                label="Choose one or more constraint functions for your optimal portfolio.",
                options=ConstraintName,
            )
        ]

    def set_objectives(self) -> None:
        """Set the objectives from the obejctives name."""
        with st.expander("Objectives configuration."):
            for obj in self.objective_names:
                st.number_input(
                    f"Enter {obj} weight",
                    min_value=0.1,
                    max_value=1.0,
                    step=0.1,
                    value=0.5,
                )

    def set_rebalance_frquency(self) -> None:
        """Set the objectives name."""
        self.rebalance_frequency = RebalanceFrequency[
            self._from_selectbox(
                label="Choose the rebalance frequency for the backtest.",
                options=RebalanceFrequency,
                is_value=False,
            )
        ]

    def get_optifolio(self) -> Optifolio:
        """Get the optifolio instance."""
        return Optifolio(
            objectives=[objective_mapping[ObjectiveName(o)] for o in self.objective_names],
            universe_name=self.universe_name,
            market_data=self.market_data or MarketData(),
        )

    def run_optimization(self) -> None:
        """Run the optifolio solve."""
        if st.button(label="COMPUTE OPTIMAL PORTFOLIO"):
            opt = self.get_optifolio()
            with st.spinner("Optimization in progress"):
                try:
                    opt_ptf = opt.solve(
                        start_date=self.start_date,
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
                    figure_or_data=opt_ptf.history_plot(start_date=self.start_date),
                    use_container_width=True,
                )

    def run_backtest(self) -> None:
        """Run the backtester."""
        if st.button(label="BACKTEST STRATEGY"):
            opt = self.get_optifolio()
            with st.spinner("Backtest in progress"):
                backtester = Backtester(
                    opt=opt,
                    start=self.start_date,
                    rebal_freq=self.rebalance_frequency,
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

    @staticmethod
    def _display_value_in_container(description: str, value: str | list) -> None:
        """Display the value in an expander container."""
        with st.expander(description.title(), expanded=True):
            if isinstance(value, str):
                st.write(value)
            elif isinstance(value, list):
                for v in value:
                    st.write(v)
            else:
                raise ValueError(f"value must be either a str or a list of str, not {type(value)}")

    def display_optifolio_problem(self) -> None:
        """Display optimization problem."""
        with st.sidebar:
            st.header("Optimization Problem")
            self._display_value_in_container(
                description="investment universe",
                value=self.universe_name.value,
            )
            self._display_value_in_container(
                description="start date",
                value=str(self.start_date.date()),
            )
            self._display_value_in_container(
                description="objectives",
                value=self.objective_names,
            )
            self._display_value_in_container(
                description="constraints",
                value=self.constraint_names,
            )

    def display_alpaca_account_sidebar(self) -> None:
        """Display alpaca account in the page sidebar."""
        with st.sidebar:
            st.header("🦙 Alpaca Account")
            st.write("The default data come from my personal Alpaca trading sandbox API keys.")
            st.markdown(
                """
                [You can find your api keys here](https://alpaca.markets/docs/trading/getting_started/#creating-an-alpaca-account-and-finding-your-api-keys)
                and enter them below to use your account 👇"""
            )
            self.set_api_keys()

    @staticmethod
    def display_in_columns(
        description: str,
        value: str,
    ) -> None:
        """Display a description next to a value."""
        col1, col2 = st.columns(2)
        with col1:
            st.write(description)
        with col2:
            st.write(value)
