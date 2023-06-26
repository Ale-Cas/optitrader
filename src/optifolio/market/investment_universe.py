"""Investment Universe module."""

from enum import Enum

from optifolio.market.market_data import MarketData


class UniverseName(str, Enum):
    """Supported universe names."""

    POPULAR_STOCKS = "POPULAR_STOCKS"


class InvestmentUniverse:
    """Class that implements an investment universe."""

    def __init__(
        self,
        tickers: tuple[str, ...] | None = None,
        name: UniverseName | None = None,
        top_market_cap: int | None = None,
        market_data: MarketData | None = None,
    ) -> None:
        assert (
            sum(param is not None for param in [tickers, name, top_market_cap]) == 1
        ), "Only one of tickers, name, or top_market_cap must be provided."
        if tickers:
            self.tickers = tickers
        elif name:
            univ_name_mapping: dict[UniverseName, tuple[str, ...]] = {
                UniverseName.POPULAR_STOCKS: (
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
            }
            self.tickers = univ_name_mapping[name]
        elif top_market_cap:
            assert isinstance(
                market_data, MarketData
            ), "Market data must be set to get the market cap."
            raise NotImplementedError
        else:
            raise AssertionError("You must pass either tickers, name or top_market_cap parameters.")
