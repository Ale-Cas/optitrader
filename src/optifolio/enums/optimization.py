"""All optimization related Enums."""

from optifolio.enums.iterable import IterEnum


class ConstraintName(IterEnum):
    """Support constraints."""

    SUM_TO_ONE = "Weights must sum to one"
    LONG_ONLY = "No shortselling allowed"
    NUMER_OF_ASSETS = "Number of assets in portfolio"
    WEIGHTS_PCT = "Weights (%) in portfolio"


class ObjectiveName(IterEnum):
    """Supported objectives names."""

    CVAR = "Conditional Value at Risk"
    COVARIANCE = "Covariance"
    EXPECTED_RETURNS = "Expected Return"
    MEAN_ABSOLUTE_DEVIATION = "Mean Absolute Deviation"
