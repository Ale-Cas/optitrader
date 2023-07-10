"""All market data related Enums."""
from optifolio.enums import IterEnum


class DataProvider(IterEnum):
    """Supported data providers for market data."""

    ALPACA = "ALPACA"
    YAHOO = "YAHOO"


class BarsField(IterEnum):
    """Possile fields in the bars from the data provider."""

    OPEN = "open"
    HIGH = "high"
    LOW = "low"
    CLOSE = "close"
    VOLUME = "volume"


class UniverseName(IterEnum):
    """Supported universe names."""

    FAANG = "FAANG Stocks (Facebook, Apple, Amazon, Google & Netflix)"
    POPULAR_STOCKS = "Most Popular Stocks"
    NASDAQ = "NASDAQ 100"
    SP500 = "Standard & Poor 500"
