"""AssetModel base model."""
from datetime import date
from enum import Enum
from typing import Any

import pandas as pd
from alpaca.trading import AssetClass, AssetExchange, AssetStatus
from pydantic import BaseModel, ConfigDict, model_validator

from optitrader.utils import clean_string


class _YahooFinnhubCommon(BaseModel):
    """Model for common fields between yahoo query and finnhub API."""

    name: str | None = None
    industry: str | None = None
    website: str | None = None
    number_of_shares: int | None = None


class YahooAssetModel(_YahooFinnhubCommon):
    """Model to represent asset info from Yahoo query."""

    sector: str | None = None
    business_summary: str | None = None


class FinnhubAssetModel(_YahooFinnhubCommon):
    """Model to represent company_profile2 info from Finhub API."""

    country: str
    currency: str
    logo: str
    ipo: date
    ticker: str


class AssetModel(FinnhubAssetModel, YahooAssetModel):
    """Model to represent an asset."""

    model_config = ConfigDict(from_attributes=True)

    weight_in_ptf: float | None = None
    asset_class: AssetClass
    symbol: str | None = None
    exchange: AssetExchange
    status: AssetStatus
    tradable: bool
    marginable: bool
    fractionable: bool

    @model_validator(mode="before")
    @classmethod
    def validate_ticker_symbol(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validate ticker vs symbol conflict."""
        if isinstance(values, dict):
            ticker = values.get("ticker", None)
            symbol = values.get("symbol", None)
            if (ticker and symbol) and ticker != symbol or not symbol:
                values["symbol"] = ticker
        return values

    def to_series(self) -> pd.Series:
        """Cast to series."""
        return pd.Series(
            {
                clean_string(k).title(): clean_string(str(v))
                if not isinstance(v, Enum)
                else clean_string(v.value).title()
                for k, v in self.model_dump(
                    exclude={"weight_in_ptf", "business_summary", "logo"}
                ).items()
                if k not in {"ipo", "ticker"}
            },
            name="",
        )
