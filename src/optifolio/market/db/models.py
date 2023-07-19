"""Database models."""
from datetime import datetime
from typing import Any

from alpaca.trading import AssetClass, AssetExchange, AssetStatus
from sqlalchemy import Boolean, Column, Date, DateTime, Enum, Integer, String
from sqlalchemy.orm import declarative_base

# metadata_ = MetaData(schema="market")
# Base = declarative_base(metadata=metadata_)
Base = declarative_base()


class Asset(Base):  # type: ignore
    """The storage model for an asset."""

    __tablename__ = "assets"

    _id = Column("id", Integer, primary_key=True, index=True)

    ticker = Column("ticker", String, unique=True, index=True)
    name = Column("name", String)
    sector = Column("sector", String)
    industry = Column("industry", String)
    website = Column("website", String)
    business_summary = Column("business_summary", String)
    number_of_shares = Column("number_of_shares", Integer)
    country = Column("country", String)
    currency = Column("currency", String)
    logo = Column("logo", String)
    ipo = Column("ipo", Date)
    tradable = Column("tradable", Boolean)
    marginable = Column("marginable", Boolean)
    fractionable = Column("fractionable", Boolean)
    status: Column[AssetStatus] = Column("status", Enum(AssetStatus))
    exchange: Column[AssetExchange] = Column("exchange", Enum(AssetExchange))
    asset_class: Column[AssetClass] = Column("asset_class", Enum(AssetClass))

    updated_at = Column("updated_at", DateTime, default=datetime.utcnow)
    updated_by = Column("updated_by", String, default="system")

    def __repr__(self) -> str:
        """Representation of the asset database model."""
        attributes = ", ".join(
            f"{attr}='{value}'" for attr, value in vars(self).items() if attr[0] != "_"
        )
        return f"<Asset({attributes})>"

    def to_dict(self) -> dict[str, Any]:
        """To dictionary."""
        return {k: v for k, v in vars(self).items() if k[0] != "_"}
