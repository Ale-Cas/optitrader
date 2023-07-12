"""Test news module."""
import pandas as pd
import pytest

from optifolio.market.news import AlpacaNewsAPI

news_client = AlpacaNewsAPI()


def test_get_news() -> None:
    """Test get_news method."""
    test_ticker: tuple[str, ...] = ("AAPL",)
    limit = 2
    news = news_client.get_news(tickers=test_ticker, limit=limit)
    assert isinstance(news, list)
    assert len(news) == limit
    assert news[0].symbols[0] == test_ticker[0]


def test_get_news_df() -> None:
    """Test get_news_df method."""
    test_ticker: tuple[str, ...] = ("AAPL",)
    news = news_client.get_news_df(tickers=test_ticker)
    assert isinstance(news, pd.DataFrame)


@pytest.mark.vcr()
def test_get_news_between_dates(
    test_tickers: tuple[str, ...],
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test get_news method."""
    news = news_client.get_news(
        tickers=test_tickers,
        start=test_start_date,
        end=test_end_date,
    )
    assert isinstance(news, list)


def test_get_news_df_between_dates(
    test_tickers: tuple[str, ...],
    test_start_date: pd.Timestamp,
    test_end_date: pd.Timestamp,
) -> None:
    """Test get_news_df method."""
    news = news_client.get_news_df(
        tickers=test_tickers,
        start=test_start_date,
        end=test_end_date,
    )
    assert isinstance(news, pd.DataFrame)
