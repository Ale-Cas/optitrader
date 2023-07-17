"""AssetModel base model."""
from datetime import date
from enum import Enum
from typing import Any

import pandas as pd
from alpaca.trading import AssetClass, AssetExchange, AssetStatus
from pydantic import BaseModel, Field, root_validator

from optifolio.utils import clean_string


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

    industry: str = Field(alias="finnhubIndustry")
    website: str = Field(alias="weburl")
    number_of_shares: int = Field(alias="shareOutstanding")
    country: str
    currency: str
    logo: str
    ipo: date
    name: str = Field(alias="finnhub_name")
    ticker: str


class AssetModel(FinnhubAssetModel, YahooAssetModel):
    """Model to represent an asset."""

    weight_in_ptf: float | None = None
    asset_class: AssetClass
    name: str
    symbol: str
    exchange: AssetExchange
    status: AssetStatus
    tradable: bool
    marginable: bool
    fractionable: bool

    @root_validator()
    def validate_ticker_symbol(cls, values: dict[str, Any]) -> dict[str, Any]:  # noqa: N805
        """Validate ticker vs symbol conflict."""
        ticker = values.get("ticker", None)
        symbol = values.get("symbol", None)
        if (ticker and symbol) and ticker != symbol:
            values["symbol"] = ticker
        return values

    class Config:
        """Configuration."""

        orm_mode = True

    def to_series(self) -> pd.Series:
        """Cast to series."""
        return pd.Series(
            {
                clean_string(k).title(): clean_string(str(v))
                if not isinstance(v, Enum)
                else clean_string(v.value).title()
                for k, v in self.dict(exclude={"weight_in_ptf", "business_summary", "logo"}).items()
                if k not in {"ipo", "ticker"}
            },
            name="",
        )
