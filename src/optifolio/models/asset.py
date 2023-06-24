"""AssetModel base model."""
from alpaca.trading import AssetClass, AssetExchange, AssetStatus
from pydantic import BaseModel


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
