"""Backtester enums."""

from optitrader.enums.iterable import IterEnum


class RebalanceFrequency(IterEnum):
    """Supported rebalance frequencies."""

    WEEKLY = "W"
    MONTHLY = "ME"
    QUARTERLY = "3M"
    YEARLY = "12M"
