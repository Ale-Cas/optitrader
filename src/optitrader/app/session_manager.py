"""Streamlit session manager."""

import logging
from functools import partial

import pandas as pd
import plotly.express as px
import streamlit as st
from alpaca.trading import TradeAccount

from optitrader import MarketData, Optitrader, Portfolio
from optitrader.backtester import Backtester, Portfolios
from optitrader.enums import (
    ConstraintName,
    IterEnum,
    ObjectiveName,
    RebalanceFrequency,
    UniverseName,
)
from optitrader.enums.market import BalanceSheetItem, CashFlowItem, IncomeStatementItem
from optitrader.market.investment_universe import InvestmentUniverse
from optitrader.market.trading import AlpacaTrading
from optitrader.optimization.constraints import ConstraintsMap
from optitrader.optimization.objectives import ObjectivesMap
from optitrader.utils.utils import remove_punctuation

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
        self.market_data: MarketData = MarketData()
        self.trader: AlpacaTrading = AlpacaTrading()
        self.universe_name = UniverseName.FAANG
        self.objective_names = [ObjectiveName.CVAR]
        self.obj_map = ObjectivesMap()
        self.constraint_names = [ConstraintName.SUM_TO_ONE, ConstraintName.LONG_ONLY]
        self.constr_map = ConstraintsMap(constraint_names=self.constraint_names)
        self.start_date = pd.Timestamp.today() - pd.Timedelta(value=365 * 2, unit="day")
        self.rebalance_frequency = RebalanceFrequency.MONTHLY
        self._opt_ptf: Portfolio | None = None
        self._ptfs: list[Portfolio] | None = None
        self._backtest_history: pd.Series | None = None
        self._ticker: str = "AAPL"
        self.tickers = InvestmentUniverse(name=self.universe_name).tickers

    def set_market_data(self, market_data: MarketData) -> None:
        """Set the market_data connection."""
        self.market_data = market_data

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

    def _clean_opt_ptf(
        self,
    ) -> None:
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
        self,
        label: str,
        options: type[IterEnum],
        default: list | None = None,
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
            # self.trader = AlpacaTrading(
            #     api_key=api_key,
            #     secret_key=secret_key,
            #     paper=True,  # TODO: make the user choose
            # )

    def _holdings_to_st(self, holdings_df: pd.DataFrame) -> None:
        """Display holdings df in streamlit."""
        key_cols = [
            "logo",
            "ticker",
            "name",
            "weight_in_ptf",
        ]
        cols_to_ignore = ["updated_at", "updated_by", "id"]
        st.dataframe(
            holdings_df,
            column_order=[
                *key_cols,
                *(c for c in holdings_df.columns if c not in key_cols and c not in cols_to_ignore),
            ],
            column_config={
                "logo": st.column_config.ImageColumn("logo", help="Company Logo", width="small")
            },
            hide_index=False,
            use_container_width=True,
        )

    def _orders_to_st(self, orders_df: pd.DataFrame) -> None:
        """Display orders df in streamlit."""
        st.dataframe(
            orders_df,
            column_order=[
                "created_at",
                "side",
                "notional",
                "qty",
                "status",
                "type",
                "time_in_force",
                "filled_at",
                "filled_qty",
            ],
            column_config={
                "notional": st.column_config.NumberColumn(
                    "notional ($)",
                    help="The notional value of the order in USD",
                    min_value=0,
                    max_value=1e9,
                    step=0.01,
                    format="$%d",
                ),
                "created_at": st.column_config.DatetimeColumn(
                    "created",
                    format="D MMM YYYY, h:mm a",
                    step=1,
                ),
                "filled_at": st.column_config.DatetimeColumn(
                    "filled",
                    format="D MMM YYYY, h:mm a",
                    step=1,
                ),
            },
            use_container_width=True,
        )

    def display_trader_portfolio(self) -> None:
        """Display the user portfolio using Alpaca trading API positions."""
        _max_expanded_len = 20
        _monetary_precision = 2
        acct = self.trader.get_account()
        assert isinstance(acct, TradeAccount)
        bp = acct.buying_power
        assert bp
        st.subheader("Current Portfolio")
        st.text(f"Connected to account # {acct.account_number}")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💵 Buying power", value=round(float(bp), _monetary_precision))
        with col2:
            assert acct.equity is not None
            assert acct.last_equity is not None
            ac_equity = round(float(acct.equity), _monetary_precision)
            equity_change = round(
                ac_equity - round(float(acct.last_equity), _monetary_precision), _monetary_precision
            )
            st.metric("💵 Equity", value=ac_equity, delta=equity_change or None)
        ptf = self.trader.get_portfolio()
        holdings_df = ptf.get_holdings_df()
        if not holdings_df.empty:
            with col1:
                tab1, tab2 = st.tabs(
                    [
                        f"This portfolio past performance since {self.start_date.date()}",
                        "Your account performance so far",
                    ]
                )
                with tab1:
                    st.plotly_chart(
                        figure_or_data=ptf.history_plot(
                            start_date=self.start_date,
                            title="",
                        ),
                        use_container_width=True,
                    )
                with tab2:
                    st.plotly_chart(
                        self.trader.get_account_portfolio_history_plot(),
                        use_container_width=True,
                    )
            with col2:
                st.plotly_chart(
                    figure_or_data=ptf.pie_plot(title=""),
                    use_container_width=True,
                )
            with st.expander("Positions", expanded=len(holdings_df) < _max_expanded_len):
                self._holdings_to_st(holdings_df)
        orders_df = self.trader.get_orders_df()
        if not orders_df.empty:
            with st.expander("Orders", expanded=len(orders_df) < _max_expanded_len):
                self._orders_to_st(orders_df)

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
        self.obj_map.reset_objectives_names(self.objective_names)

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
        self.constr_map.reset_constraint_names(self.constraint_names)

    def set_objectives(self) -> None:
        """Set the objectives from the obejctives name."""
        st.sidebar.subheader("🎯 Objectives")
        _min = 0.1
        for obj in self.objective_names:
            with st.expander(obj, expanded=False):
                st.write(self.obj_map.get_obj_doc(ObjectiveName(obj)))
                latex = self.obj_map.get_obj_latex(ObjectiveName(obj))
                if latex:
                    st.latex(latex)
                self.obj_map.add_objective(
                    name=obj,
                    weight=st.number_input(
                        f"Enter `{obj}` weight",
                        min_value=_min,
                        max_value=_min * 1e2,
                        step=_min,
                        value=_min,
                        key=obj,
                        on_change=self._clean_opt_ptf,
                    ),
                )

    def set_constraints(self) -> None:
        """Set the constraints from the obejctives name."""
        st.sidebar.subheader("🎛️ Constraints")
        for con in self.constraint_names:
            if con.is_bounded:
                with st.expander(con):
                    st.write(f"{con} docs")
                    lower_bound = int(
                        st.number_input(
                            f"`{con.title()}` minimum",
                            min_value=1,
                            max_value=10,
                            step=1,
                            value=2,
                            on_change=self._clean_opt_ptf,
                        )
                    )
                    upper_bound = int(
                        st.number_input(
                            f"`{con.title()}` maximum",
                            min_value=1,
                            max_value=100,
                            step=1,
                            value=50,
                            on_change=self._clean_opt_ptf,
                        )
                    )
                    self.constr_map.set_constraint_bounds(
                        name=con,
                        lower_bound=lower_bound,
                        upper_bound=upper_bound,
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

    def get_optitrader(self) -> Optitrader:
        """Get the optitrader instance."""
        return Optitrader(
            objectives=self.obj_map.objectives,
            constraints=self.constr_map.constraints,
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
                holdings_df = self._opt_ptf.get_holdings_df()
                self._holdings_to_st(holdings_df)
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
        """Run the optitrader solve."""
        opt = self.get_optitrader()
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
        """Run the optitrader solve."""
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
            opt = self.get_optitrader()
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
                    title="Out of sample strategy wealth from start date to today",
                ),
                use_container_width=True,
            )
        if self._ptfs:
            st.write("Portfolios allocation over time")
            st.dataframe(
                Portfolios(self._ptfs)
                .to_df()
                .sort_index(ascending=False)
                .style.background_gradient(cmap="Blues", axis=1)
            )

    def display_financials(self) -> None:
        """Display the financials."""
        st.markdown("#### Financial statements over time")
        fin_df = self.market_data.get_financials(self.ticker)
        statements: dict[str, list[IterEnum]] = {
            "Income Statement": [
                IncomeStatementItem.REVENUE,
                IncomeStatementItem.NET_INCOME,
            ],
            "Balance Sheet": [BalanceSheetItem.ASSETS, BalanceSheetItem.LIABILITIES],
            "Cash Flow": [CashFlowItem.FREE, CashFlowItem.OPERATING],
        }
        tabs = st.tabs(list(statements.keys()))
        for _idx, tab in enumerate(tabs):
            statement = list(statements.keys())[_idx]
            fin_df_tab = fin_df[statements[statement]]
            with tab:
                st.plotly_chart(
                    figure_or_data=px.bar(
                        data_frame=fin_df_tab,
                        barmode="group",
                        labels={"asOfDate": "Date", "value": "💵   U.S. Dollars"},
                        title=statement,
                    ),
                    use_container_width=True,
                )

    def display_news(self) -> None:
        """Display the news."""
        asset = self.market_data.get_asset_from_ticker(self.ticker)
        if asset.name:
            name = remove_punctuation(asset.name.split()[0].title())
        else:
            log.warning(f"Asset not found for ticker: {asset.ticker}")
            name = asset.ticker
        st.markdown(f"## Latest {name} News")

        num_res = int(
            st.sidebar.number_input(
                "Number of news articles",
                min_value=1,
                max_value=10,
                value=3,
                step=1,
            )
        )
        news = self.market_data.get_news((self.ticker,), limit=num_res)
        for n in news:
            if self.ticker in n.symbols:
                st.markdown(f"#### {n.headline}")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"_{n.author}_")
                with col2:
                    st.write(n.created_at)
                with st.expander("🗞️📰 Full article 👇🏻"):
                    st.write(n.content, unsafe_allow_html=True)

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

    def display_optitrader_problem(self) -> None:
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

    def invest_in_optimal_portfolio(self) -> None:
        """Handle how to invest in the optimal portfolio."""
        if self._opt_ptf:
            bp = self.trader.account.non_marginable_buying_power
            if bp:
                amount = round(
                    st.sidebar.number_input(
                        "Investment amount in USD $",
                        min_value=10.0,
                        max_value=round(number=float(bp), ndigits=2),
                        value=round(number=float(bp) / 5.0, ndigits=1),
                        step=0.1,
                    ),
                    2,
                )
        orders = None
        if st.button(label="INVEST IN PORTFOLIO", disabled=self._opt_ptf is None) and self._opt_ptf:
            with st.spinner("Sending orders..."):
                orders = self.trader.invest_in_portfolio(portfolio=self._opt_ptf, amount=amount)
                st.success("Orders submitted successfully!", icon="✅")
        if self._opt_ptf and orders:
            self._orders_to_st(pd.DataFrame([o.dict() for o in orders]).set_index("symbol"))
