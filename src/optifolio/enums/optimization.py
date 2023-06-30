"""All optimization related Enums."""

from optifolio.enums.iterable import IterEnum


class ConstraintName(IterEnum):
    """Support constraints."""

    SUM_TO_ONE = "SUM_TO_ONE"
    LONG_ONLY = "LONG_ONLY"
    NUMER_OF_ASSETS = "NUMER_OF_ASSETS"
    WEIGHTS_PCT = "WEIGHTS_PCT"


class ObjectiveName(IterEnum):
    """Supported objectives names."""

    CVAR = "Conditional Value at Risk"
    COVARIANCE = "Covariance"
    EXPECTED_RETURNS = "Expected Return"
    MEAN_ABSOLUTE_DEVIATION = "Mean Absolute Deviation"
