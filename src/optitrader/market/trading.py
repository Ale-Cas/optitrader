"""Trading module."""
import logging

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from alpaca.common import APIError
from alpaca.trading import Order, TradeAccount, TradingClient
from alpaca.trading.requests import GetOrdersRequest, QueryOrderStatus
from typeguard import typechecked

from optitrader.config import SETTINGS
from optitrader.market.market_data import MarketData
from optitrader.portfolio import Portfolio

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class AlpacaTrading(TradingClient):
    """Class to interact with Alpaca trading API."""

    def __init__(
        self,
        api_key: str | None = None,
        secret_key: str | None = None,
        paper: bool = True,
    ) -> None:
        super().__init__(
            api_key or SETTINGS.ALPACA_TRADING_API_KEY,
            secret_key=secret_key or SETTINGS.ALPACA_TRADING_API_SECRET,
            paper=paper,
        )
        self.market_data = MarketData(
            trading_key=api_key or SETTINGS.ALPACA_TRADING_API_KEY,
            trading_secret=secret_key or SETTINGS.ALPACA_TRADING_API_SECRET,
        )

    @property
    def account(self) -> TradeAccount:
        """Get the account."""
        account = self.get_account()
        assert isinstance(account, TradeAccount)
        return account

    def get_portfolio(self) -> Portfolio:
        """Get Portfolio from starting positions."""
        pos = self.get_all_positions()
        assert isinstance(pos, list)
        _pos_series = pd.Series({p.symbol: float(p.market_value) for p in pos})
        return Portfolio(weights=_pos_series / _pos_series.sum(), market_data=self.market_data)

    def get_account_portfolio_history(self) -> pd.DataFrame:
        """
        Get the account portfolio history from Alpaca.

        See more: https://alpaca.markets/docs/api-references/trading-api/portfolio-history/
        """
        df = pd.DataFrame(self.get("/account/portfolio/history?timeframe=1D"))
        _idx = "timestamp"
        df[_idx] = pd.to_datetime(df[_idx], unit="s").dt.date
        df.set_index(_idx, inplace=True)
        df.drop(columns=["base_value", "timeframe"], inplace=True)
        return df

    def get_account_portfolio_history_plot(self) -> go.Figure:
        """Get the plot of the account portfolio history."""
        history = self.get_account_portfolio_history()["equity"]
        return px.line(
            data_frame=history,
            x=history.index,
            y=history.values,
            labels={"timestamp": "", "y": ""},
            title="",
        )

    def get_orders_df(self, status: QueryOrderStatus = QueryOrderStatus.ALL) -> pd.DataFrame:
        """Get the account orders in a df."""
        orders = self.get_orders(
            GetOrdersRequest(
                limit=500,  # current max
                status=status,
            )
        )
        assert isinstance(orders, list)
        _idx = "symbol"
        df = pd.DataFrame([o.dict() for o in orders])
        if _idx in df.columns:
            return df.set_index(["symbol"])
        return df

    @typechecked
    def invest_in_portfolio(
        self, portfolio: Portfolio, amount: float, fail_on_error: bool = False
    ) -> list[Order]:
        """Invest a certain amount in a portfolio."""
        bp = self.account.buying_power
        assert bp, "No buying power in the account."
        _bp = round(number=float(bp), ndigits=2)
        amount = round(number=float(amount), ndigits=2)
        assert (
            _bp > amount
        ), f"The passed `amount` {amount} is greater then the account buying power {_bp}"
        acct = self.get_account()
        assert isinstance(acct, TradeAccount)
        orders_resp = []
        for order in portfolio.to_orders_list(amount=amount):
            try:
                resp = self.submit_order(order)
                assert isinstance(resp, Order)
                orders_resp.append(resp)
            except APIError as alpaca_api_error:
                log.warning(order.symbol)
                log.warning(order.notional)
                log.warning(acct.buying_power)
                log.warning(alpaca_api_error)
                if fail_on_error:
                    raise AssertionError(
                        f"Order to {order.side} {order.notional} $ of {order.symbol} failed!"
                    ) from alpaca_api_error
        return orders_resp
