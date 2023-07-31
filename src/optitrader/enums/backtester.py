"""Backtester enums."""
from optitrader.enums.iterable import IterEnum


class RebalanceFrequency(IterEnum):
    """Supported rebalance frequencies."""

    WEEKLY = "W"
    MONTHLY = "M"
    QUARTERLY = "3M"
    YEARLY = "12M"
