"""Backtester enums."""
from optifolio.enums.iterable import IterEnum


class RebalanceFrequency(IterEnum):
    """Supported rebalance frequencies."""

    DAILY = "D"
    WEEKLY = "W"
    MONTHLY = "M"
    QUARTERLY = "3M"
    YEARLY = "12M"
