"""Test trading module."""

from unittest.mock import patch

import pandas as pd
import pytest
from alpaca.common import APIError
from alpaca.trading import TradeAccount

from optifolio.market.trading import AlpacaTrading
from optifolio.portfolio import Portfolio

trader = AlpacaTrading()


def test_account() -> None:
    """Test account."""
    assert isinstance(trader.account, TradeAccount)


@pytest.mark.vcr()
def test_get_account_portfolio_history() -> None:
    """Test get_account_portfolio_history method."""
    history = trader.get_account_portfolio_history()
    assert isinstance(history, pd.DataFrame)


@pytest.mark.vcr()
def test_get_orders_df() -> None:
    """Test get_orders_df method."""
    orders_history = trader.get_orders_df()
    assert isinstance(orders_history, pd.DataFrame)


def test_get_orders_empty_df() -> None:
    """Test get_orders_df method with a mock empty df."""
    with patch("optifolio.market.trading.AlpacaTrading.get_orders", return_value=[]):
        orders_history = trader.get_orders_df()
        assert isinstance(orders_history, pd.DataFrame)
        assert orders_history.empty


@pytest.mark.vcr()
def test_invest_in_portfolio(mock_ptf: Portfolio) -> None:
    """Test invest_in_portfolio method."""
    orders = trader.invest_in_portfolio(portfolio=mock_ptf, amount=10)
    assert isinstance(orders, list)


def test_invest_in_portfolio_api_error() -> None:
    """Test invest_in_portfolio method."""
    with patch(
        "optifolio.market.trading.AlpacaTrading.submit_order",
        side_effect=APIError(error="Mock error"),
    ):
        trader.invest_in_portfolio(
            portfolio=Portfolio(
                weights=pd.Series(
                    {
                        "MSFT": 1.0,
                    }
                ),
            ),
            amount=10,
        )


def test_invest_in_portfolio_fail_on_api_error() -> None:
    """Test invest_in_portfolio method."""
    with patch(
        "optifolio.market.trading.AlpacaTrading.submit_order",
        side_effect=APIError(error="Mock error"),
    ), pytest.raises(AssertionError):
        trader.invest_in_portfolio(
            portfolio=Portfolio(
                weights=pd.Series(
                    {
                        "MSFT": 1.0,
                    }
                ),
            ),
            amount=10,
            fail_on_error=True,
        )
