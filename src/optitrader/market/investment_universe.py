"""Investment Universe module."""
from functools import lru_cache

import pandas as pd
from pydantic import BaseModel

from optitrader.enums import UniverseName


class _WikiScrapeRequest(BaseModel):
    """Universe scraped info."""

    html_index: int
    url_path: str
    column_name: str


class InvestmentUniverse:
    """Class that implements an investment universe."""

    SCRAPED_UNIV = (UniverseName.NASDAQ, UniverseName.SP500)

    def __init__(
        self,
        tickers: tuple[str, ...] | None = None,
        name: UniverseName | None = None,
    ) -> None:
        assert tickers or name, "Only one of tickers or name must be provided."
        if tickers:
            self.tickers = tickers
        if name:
            self.name = name
            if name in self.SCRAPED_UNIV:
                self.tickers = self.scrape_wikipedia_tickers()
            else:
                univ_name_mapping: dict[UniverseName, tuple[str, ...]] = {
                    UniverseName.FAANG: (
                        "META",  # F
                        "AAPL",  # A
                        "AMZN",  # A
                        "NFLX",  # N
                        "GOOGL",  # G
                    ),
                    UniverseName.POPULAR_STOCKS: (
                        "AAPL",
                        "AMZN",
                        "TSLA",
                        "GOOGL",
                        "BRK.B",
                        "V",
                        "JPM",
                        "NVDA",
                        "MSFT",
                        "DIS",
                        "NFLX",
                        "META",
                        "WMT",
                        "BABA",
                        "AMD",
                        "ACN",
                        "PFE",
                        "ORCL",
                        "ZM",
                        "SHOP",
                        "COIN",
                    ),
                }
                self.tickers = univ_name_mapping[name]

    def __len__(self) -> int:
        """Length of universe tickers."""
        return len(self.tickers)

    @lru_cache  # noqa: B019
    def scrape_wikipedia_tickers(self) -> tuple[str, ...]:
        """Scrape wikixpedia.com for universe name tickers."""
        assert self.name, "The name must be set to use this method."
        assert self.name in self.SCRAPED_UNIV, f"The name must be one of {self.SCRAPED_UNIV}."
        _scraped_univ_map: dict[UniverseName, _WikiScrapeRequest] = {
            UniverseName.NASDAQ: _WikiScrapeRequest(
                html_index=4,
                url_path="Nasdaq-100",
                column_name="Ticker",
            ),
            UniverseName.SP500: _WikiScrapeRequest(
                html_index=0,
                url_path="List_of_S%26P_500_companies",
                column_name="Symbol",
            ),
        }
        params = _scraped_univ_map[self.name]
        # TODO: these tables have a lot of information such as changes, GICS sectors and industries and name
        _html = pd.read_html(f"https://en.wikipedia.org/wiki/{params.url_path}", flavor="html5lib")
        tickers: tuple[str, ...] = tuple(_html[params.html_index][params.column_name])
        # basic validation on the tickers
        for t in tickers:
            assert isinstance(t, str), f"Found ticker {t} that's not a string."
            assert t.isupper(), f"Found ticker {t} that's not upper case."
        return tickers
