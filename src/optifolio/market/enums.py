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
