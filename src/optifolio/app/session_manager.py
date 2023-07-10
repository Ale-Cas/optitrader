"""Streamlit session manager."""

import logging
from functools import partial

import pandas as pd
import plotly.express as px
import streamlit as st

from optifolio import MarketData, Optifolio, Portfolio
from optifolio.backtester import Backtester, Portfolios
from optifolio.enums import (
    ConstraintName,
    IterEnum,
    ObjectiveName,
    RebalanceFrequency,
    UniverseName,
)
from optifolio.market.investment_universe import InvestmentUniverse
from optifolio.optimization.objectives import ObjectivesMap

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class SessionManager:
    """
    Streamlit session manager.

    Attributes
    ----------
    `ticker`: str =
    `market_data`: MarketData | None = None
    `universe_name` = UniverseName.FAANG
    `objective_names` = [ObjectiveName.CVAR]
    `constraint_names` = [ConstraintName.SUM_TO_ONE, ConstraintName.LONG_ONLY]
    `start_date` = pd.Timestamp.today() - pd.Timedelta(value=365 * 2, unit="day")
    `rebalance_frequency` = RebalanceFrequency.MONTHLY
    `_opt_ptf`: Portfolio | None = None
    `_ptfs`: list[Portfolio] | None = None
    `_backtest_history`: pd.Series | None = None
    """

    def __init__(self) -> None:
        """Initialize a Streamlit session object."""
        self.market_data: MarketData | None = None
        self.universe_name = UniverseName.FAANG
        self.objective_names = [ObjectiveName.CVAR]
        self.obj_map = ObjectivesMap()
        self.constraint_names = [ConstraintName.SUM_TO_ONE, ConstraintName.LONG_ONLY]
        self.start_date = pd.Timestamp.today() - pd.Timedelta(value=365 * 2, unit="day")
        self.rebalance_frequency = RebalanceFrequency.MONTHLY
        self._opt_ptf: Portfolio | None = None
        self._ptfs: list[Portfolio] | None = None
        self._backtest_history: pd.Series | None = None
        self._ticker: str = "AAPL"
        self.tickers = InvestmentUniverse(name=self.universe_name).tickers

    @property
    def ticker(self) -> str:
        """Explore page ticker."""
        return self._ticker.upper()

    def set_ticker(self, ticker: str) -> None:
        """Set the ticker."""
        self._ticker = ticker

    def set_tickers(self, universe_name: str) -> None:
        """Get the universe tickers."""
        self.tickers = InvestmentUniverse(name=UniverseName(universe_name)).tickers

    def display_tickers(self) -> None:
        """Display the tickers in the universe."""
        tickers = sorted(self.tickers)
        tickers_per_row = 10
        len_tickers = len(tickers)
        with st.expander(
            f"{self.universe_name} universe tickers", expanded=len_tickers < tickers_per_row
        ):
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

    def _clean_opt_ptf(self) -> None:
        """Clean the optimal portfolio cache."""
        self._opt_ptf = None

    def _clean_backtest_results(self) -> None:
        """Clean the optimal portfolio cache."""
        self._ptfs = None
        self._backtest_history = None

    def _change_universe(self, universe_name: str) -> None:
        """Clean the optimal portfolio cache and reset the."""
        self._clean_opt_ptf()
        self._clean_backtest_results()
        self.set_tickers(universe_name)

    def _from_selectbox(
        self,
        label: str,
        options: type[IterEnum],
        value: str,
        is_value: bool = True,
    ) -> str:
        """Return the selected value from the selectbox."""
        if options == RebalanceFrequency:
            on_change = self._clean_backtest_results
        elif options == UniverseName:
            on_change = partial(self._change_universe, value)
        else:
            on_change = self._clean_opt_ptf
        sel = st.selectbox(
            label=label,
            options=options.get_values_list() if is_value else options.get_names_list(),
            index=options.get_index_of_value(value),
            on_change=on_change,
        )
        return sel or ""

    def _from_multiselect(
        self, label: str, options: type[IterEnum], default: list | None = None
    ) -> list[str]:
        """Return a list from the multiselect."""
        _opts = options.get_values_list()
        return st.multiselect(
            label=label,
            options=_opts,
            default=default,
            on_change=self._clean_opt_ptf,
        )

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
                value=self.universe_name.value,
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
                default=self.objective_names,
            )
        ]

    def set_constraint_names(self) -> None:
        """Set the constraints name."""
        self.constraint_names = [
            ConstraintName(o)
            for o in self._from_multiselect(
                label="Choose one or more constraints for your optimal portfolio.",
                options=ConstraintName,
                default=self.constraint_names,
            )
        ]

    def set_objectives(self) -> None:
        """Set the objectives from the obejctives name."""
        st.sidebar.subheader("🎯 Objectives")
        for obj in self.objective_names:
            with st.expander(obj, expanded=False):
                st.write(self.obj_map.get_obj_doc(ObjectiveName(obj)))
                self.obj_map.add_objective(
                    name=obj,
                    weight=st.number_input(
                        f"Enter `{obj}` weight",
                        min_value=0.1,
                        max_value=1.0,
                        step=0.1,
                        value=0.5,
                        key=obj,
                    ),
                )

    def set_constraints(self) -> None:
        """Set the constraints from the obejctives name."""
        st.sidebar.subheader("🎛️ Constraints")
        for con in self.constraint_names:
            if con in [ConstraintName.NUMER_OF_ASSETS, ConstraintName.WEIGHTS_PCT]:
                with st.expander(con):
                    st.write(f"{con} docs")
                    st.number_input(
                        f"`{con.title()}` minimum",
                        min_value=0.1,
                        max_value=1.0,
                        step=0.1,
                        value=0.5,
                    )
                    st.number_input(
                        f"`{con.title()}` maximum",
                        min_value=0.1,
                        max_value=1.0,
                        step=0.1,
                        value=0.5,
                    )
            else:
                with st.expander(con):
                    st.write(f"{con} documentation.")

    def set_rebalance_frequency(self) -> None:
        """Set the objectives name."""
        self.rebalance_frequency = RebalanceFrequency[
            self._from_selectbox(
                label="Choose the rebalance frequency for the backtest.",
                options=RebalanceFrequency,
                is_value=False,
                value=self.rebalance_frequency,
            )
        ]

    def get_optifolio(self) -> Optifolio:
        """Get the optifolio instance."""
        return Optifolio(
            objectives=self.obj_map.objectives,
            universe_name=self.universe_name,
            market_data=self.market_data or MarketData(),
        )

    def display_solution(self) -> None:
        """Display the solution."""
        if self._opt_ptf:
            with st.spinner("Elaborating solution"):
                st.plotly_chart(
                    figure_or_data=self._opt_ptf.pie_plot(),
                    use_container_width=True,
                )
                _cols = ["name", "weight_in_ptf"]
                holdings_df = self._opt_ptf.get_holdings_df()
                st.dataframe(
                    holdings_df,
                    column_order=[*_cols, *(c for c in holdings_df.columns if c not in _cols)],
                )
                st.plotly_chart(
                    figure_or_data=self._opt_ptf.history_plot(start_date=self.start_date),
                    use_container_width=True,
                )
                st.markdown("##### Optimal objectives details")
                col1, col2, col3 = st.columns(3)
                for o in self._opt_ptf.objective_values:
                    with col1:
                        st.markdown(f"Name: `{o.name}`")
                    with col2:
                        st.markdown(f"Weight: `{round(o.weight, 1)}`")
                    with col3:
                        st.markdown(f"Optimal value: `{round(o.value, 9)}`")

    def _run_optimization(self) -> None:
        """Run the optifolio solve."""
        opt = self.get_optifolio()
        with st.spinner("Optimization in progress"):
            try:
                opt_ptf = opt.solve(
                    start_date=self.start_date,
                    weights_tolerance=1e-3,
                )
                opt_ptf.set_market_data(opt.market_data)
                self._opt_ptf = opt_ptf
                self.set_ticker(
                    opt_ptf.get_non_zero_weights().sort_values(ascending=False).index[0]
                )
            except AssertionError as er:
                log.warning(er)
                st.error("Couldn't find a solution!")

    def run_optimization(self) -> None:
        """Run the optifolio solve."""
        if st.button(label="COMPUTE OPTIMAL PORTFOLIO"):
            if self._opt_ptf:
                st.info(
                    "You already computed an optimal portfolio, change the parameters above to discard the solution and compute a new one."
                )
            else:
                self._run_optimization()

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
                self._ptfs = backtester.compute_portfolios()
                self._backtest_history = backtester.compute_history_values()

    def display_backtest(self) -> None:
        """Display the backtester result."""
        if self._backtest_history is not None and not self._backtest_history.empty:
            st.plotly_chart(
                figure_or_data=px.line(
                    data_frame=self._backtest_history,
                    x=self._backtest_history.index,
                    y=self._backtest_history.values,
                    labels={"timestamp": "", "y": ""},
                    title="Portfolio value from start date to today",
                ),
                use_container_width=True,
            )
        if self._ptfs:
            st.write("Portfolios allocation over time")
            st.dataframe(Portfolios(self._ptfs).to_df().sort_index(ascending=False))

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
