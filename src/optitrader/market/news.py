"""News module."""

from datetime import datetime
from functools import lru_cache

from alpaca.common.rest import RESTClient
from pandas import DataFrame, Timestamp
from pydantic import BaseModel

from optitrader.config import SETTINGS


class NewsArticle(BaseModel):
    """The data model for a news article."""

    created_at: datetime
    headline: str
    author: str
    content: str
    symbols: list[str]


class AlpacaNewsAPI(RESTClient):
    """
    Alpaca Rest News API.

    See more:
    - https://github.com/Ale-Cas/optitrader/issues/19
    - https://docs.alpaca.markets/docs/news-api#get-latest-news
    """

    def __init__(
        self,
        api_key: str | None = None,
        secret_key: str | None = None,
        use_basic_auth: bool = True,
    ) -> None:
        """
        Initialize a News Data Client.

        Args:
            api_key (Optional[str], optional): Alpaca API key. Defaults to None.
            secret_key (Optional[str], optional): Alpaca API secret key. Defaults to None.
            oauth_token (Optional[str]): The oauth token if authenticating via OAuth. Defaults to None.
            use_basic_auth (bool, optional): If true, API requests will use basic authorization headers.
        """
        assert SETTINGS.is_broker, "You must set the Broker API keys to use this API."
        super().__init__(
            api_key=api_key or SETTINGS.ALPACA_BROKER_API_KEY,
            secret_key=secret_key or SETTINGS.ALPACA_BROKER_API_SECRET,
            use_basic_auth=use_basic_auth,
            api_version="v1beta1",
            base_url="https://data.sandbox.alpaca.markets",
            sandbox=True,
            raw_data=True,  # not mapped by alpaca-py
        )

    @lru_cache  # noqa: B019
    def get_news(
        self,
        tickers: tuple[str, ...],
        start: datetime | Timestamp | None = None,
        end: datetime | Timestamp | None = None,
        limit: int = 5,
        include_content: bool = True,
        exclude_contentless: bool = True,
    ) -> list[NewsArticle]:
        """Get news articles."""
        result = self.get(
            path="/news",
            data={
                "symbols": ",".join(tickers),
                "start": start.isoformat("T") + "Z" if start else None,
                "end": end.isoformat("T") + "Z" if end else None,
                "limit": limit,
                "include_content": include_content,
                "exclude_contentless": exclude_contentless,
            },
        )
        assert isinstance(result, dict), f"Result is not a dict but {type(result)}"
        return [NewsArticle(**res) for res in result["news"]]

    def get_news_df(
        self,
        tickers: tuple[str, ...],
        start: datetime | Timestamp | None = None,
        end: datetime | Timestamp | None = None,
        limit: int = 5,
        include_content: bool = True,
        exclude_contentless: bool = True,
    ) -> DataFrame:
        """Get news articles."""
        return DataFrame(
            n.dict()
            for n in self.get_news(
                tickers=tickers,
                start=start,
                end=end,
                limit=limit,
                include_content=include_content,
                exclude_contentless=exclude_contentless,
            )
        ).set_index("created_at")
