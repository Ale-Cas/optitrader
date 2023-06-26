"""Test the investment universe implementation."""

from optifolio.market import InvestmentUniverse, UniverseName


def test_investment_universe_with_name() -> None:
    """Test the investment universe initialization with the name."""
    univ = InvestmentUniverse(name=UniverseName.POPULAR_STOCKS)
    assert len(univ.tickers) == 21  # noqa: PLR2004
