"""All optimization related Enums."""

from optitrader.enums.iterable import IterEnum


class ConstraintName(IterEnum):
    """Support constraints."""

    SUM_TO_ONE = "Weights must sum to one"
    LONG_ONLY = "No shortselling allowed"
    NUMER_OF_ASSETS = "Number of assets in portfolio"
    WEIGHTS_PCT = "Weights (%) in portfolio"

    @property
    def is_bounded(self) -> bool:
        """Return true if this objective name is for a bounded constraint."""
        return self.name in ["NUMER_OF_ASSETS", "WEIGHTS_PCT"]


class ObjectiveName(IterEnum):
    """Supported objectives names."""

    MOST_DIVERSIFIED = "Maximize Diversification Ratio"
    CVAR = "Conditional Value at Risk"
    COVARIANCE = "Covariance"
    EXPECTED_RETURNS = "Expected Return"
    MEAN_ABSOLUTE_DEVIATION = "Mean Absolute Deviation"
    FINANCIALS = "Financial Statements"
