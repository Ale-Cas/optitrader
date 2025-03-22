"""Module to handle interactions with Finhub API."""

import logging
import time

import finnhub
import pandas as pd

from optitrader.config import SETTINGS
from optitrader.models.asset import FinnhubAssetModel

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)


class FinnhubClient(finnhub.Client):
    """Finhub API client."""

    def __init__(self, api_key: str | None = None):
        super().__init__(api_key=api_key or SETTINGS.FINHUB_API_KEY)

    def get_asset_profile(self, ticker: str) -> FinnhubAssetModel:
        """Get the company profile for each ticker."""
        try:
            profile = self.company_profile2(symbol=ticker)
        except finnhub.FinnhubAPIException as api_error:
            log.debug(f"Request for ticker {ticker} sleeping 1 second")
            log.debug(type(api_error))
            time.sleep(1)  # wait time limit reset
            profile = self.company_profile2(symbol=ticker)
        return FinnhubAssetModel(
            **profile,
            industry=profile["finnhubIndustry"],
            website=profile["weburl"],
            number_of_shares=int(profile["shareOutstanding"] * 1e6),
            finnhub_name=profile["name"],
        )

    def get_companies_profiles(self, tickers: tuple[str, ...]) -> list[FinnhubAssetModel]:
        """Get the company profile for each ticker."""
        profiles = []
        for i, t in enumerate(sorted(tickers)):
            try:
                profile = self.get_asset_profile(ticker=t)
            # On top of all plan's limit, there is a 30 API calls/ second limit.
            except finnhub.FinnhubAPIException as api_error:
                log.debug(f"Requests number {i + 1} for ticker {t} sleeping 60 seconds")
                log.debug(type(api_error))
                # get company profile v2 with 60 rpm
                time.sleep(60)  # wait time 1 minute for limit reset
                profile = self.get_asset_profile(ticker=t)
            except Exception:
                log.exception(f"Error getting profile for ticker {t}")
                continue
            else:
                profiles.append(profile)
        return profiles

    def get_companies_df(self, tickers: tuple[str, ...]) -> pd.DataFrame:
        """Get the dataframe of companies profiles."""
        return pd.DataFrame([a.model_dump() for a in self.get_companies_profiles(tickers)])
