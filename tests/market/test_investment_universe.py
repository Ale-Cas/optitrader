"""Test the investment universe implementation."""
import pytest

from optitrader.enums import UniverseName
from optitrader.market import InvestmentUniverse


def test_investment_universe_with_name() -> None:
    """Test the investment universe initialization with the name."""
    univ = InvestmentUniverse(name=UniverseName.POPULAR_STOCKS)
    assert len(univ.tickers) == 21  # noqa: PLR2004
    univ = InvestmentUniverse(name=UniverseName.FAANG)
    assert len(univ.tickers) == 5  # noqa: PLR2004


@pytest.mark.vcr()
def test_scrape_wikipedia_tickers() -> None:
    """Scrape tickers test."""
    tickers = InvestmentUniverse(name=UniverseName.SP500).tickers
    assert isinstance(tickers, tuple)
    assert len(tickers) >= 500  # noqa: PLR2004
    tickers = InvestmentUniverse(name=UniverseName.NASDAQ).tickers
    assert isinstance(tickers, tuple)
    assert len(tickers) >= 100  # noqa: PLR2004


def test_assertion_scrape_wikipedia_tickers() -> None:
    """Scrape tickers test."""
    with pytest.raises(expected_exception=AssertionError, match="The name must be one of"):
        InvestmentUniverse(name=UniverseName.POPULAR_STOCKS).scrape_wikipedia_tickers()
