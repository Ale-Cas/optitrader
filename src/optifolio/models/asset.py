"""AssetModel base model."""
from enum import Enum

import pandas as pd
from alpaca.trading import AssetClass, AssetExchange, AssetStatus
from pydantic import BaseModel

from optifolio.utils import clean_string


class YahooAssetModel(BaseModel):
    """Model to represent asset info from Yahoo query."""

    industry: str
    sector: str
    website: str
    total_number_of_shares: int
    business_summary: str


class AssetModel(YahooAssetModel):
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

    def to_series(self) -> pd.Series:
        """Cast to series."""
        return pd.Series(
            {
                clean_string(k).title(): clean_string(str(v))
                if not isinstance(v, Enum)
                else clean_string(v.value).title()
                for k, v in self.dict().items()
            },
            name="",
        )
