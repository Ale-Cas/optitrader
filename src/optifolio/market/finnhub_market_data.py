"""Module to handle interactions with Finhub API."""

import logging
import time
from functools import lru_cache

import finnhub
import pandas as pd

from optifolio.config import SETTINGS
from optifolio.models.asset import FinnhubAssetModel

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class FinnhubClient(finnhub.Client):
    """Finhub API client."""

    def __init__(self, api_key: str | None = None):
        super().__init__(api_key=api_key or SETTINGS.FINHUB_API_KEY)

    @lru_cache  # noqa: B019
    def get_asset_profile(self, ticker: str) -> FinnhubAssetModel:
        """Get the company profile for each ticker."""
        try:
            profile = self.company_profile2(symbol=ticker)
        except finnhub.FinnhubAPIException as api_error:
            log.warning(f"Request for ticker {ticker}")
            log.warning(api_error)
            time.sleep(1)  # wait time limit reset
            profile = self.company_profile2(symbol=ticker)
        return FinnhubAssetModel(**profile, finnhub_name=profile["name"])

    @lru_cache  # noqa: B019
    def get_companies_profiles(self, tickers: tuple[str, ...]) -> list[FinnhubAssetModel]:
        """Get the company profile for each ticker."""
        profiles = []
        for i, t in enumerate(sorted(tickers)):
            try:
                profiles.append(self.get_asset_profile(ticker=t))
            # On top of all plan's limit, there is a 30 API calls/ second limit.
            except finnhub.FinnhubAPIException as api_error:
                log.warning(f"Request number {i+1} for ticker {t}")
                log.warning(api_error)
                time.sleep(1)  # wait time limit reset
                try:
                    profiles.append(self.get_asset_profile(ticker=t))
                except finnhub.FinnhubAPIException as api_error:
                    log.warning(f"Requests number {i+1} for ticker {t}")
                    log.warning(api_error)
                    # get company profile v2 with 60 rpm
                    time.sleep(60)  # wait time 1 minute for limit reset
                    profiles.append(self.get_asset_profile(ticker=t))
        return profiles

    def get_companies_df(self, tickers: tuple[str, ...]) -> pd.DataFrame:
        """Get the dataframe of companies profiles."""
        return pd.DataFrame([a.dict() for a in self.get_companies_profiles(tickers)])
