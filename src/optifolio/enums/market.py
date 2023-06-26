"""All market data related Enums."""
from enum import Enum


class DataProvider(str, Enum):
    """Supported data providers for market data."""

    ALPACA = "ALPACA"
    YAHOO = "YAHOO"


class BarsField(str, Enum):
    """Possile fields in the bars from the data provider."""

    OPEN = "open"
    HIGH = "high"
    LOW = "low"
    CLOSE = "close"
    VOLUME = "volume"


class UniverseName(str, Enum):
    """Supported universe names."""

    FAANG = "FAANG Stocks (Facebook, Apple, Amazon, Google & Netflix)"
    POPULAR_STOCKS = "Most Popular Stocks"
    NASDAQ = "NASDAQ 100"
    SP500 = "Standard & Poor 500"
