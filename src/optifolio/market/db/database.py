"""Local SQL storage of assets table."""
import logging

import pandas as pd
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from optifolio.market.db.models import Asset, Base
from optifolio.models.asset import AssetModel

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class MarketDB:
    """Class to handle interactions with sqlite market.db database."""

    SQLALCHEMY_DATABASE_URL = "sqlite:///market.db"
    TABLE_NAME = Asset.__tablename__

    def __init__(self) -> None:
        """Initialize the market database object."""
        self.engine = create_engine(
            self.SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
        )
        self._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session: Session = self._SessionLocal()

    def create_tables(self) -> None:
        """Create the assets table."""
        with self.engine.begin() as conn:
            Base.metadata.create_all(conn)

    def drop_tables(self) -> None:
        """Drop the assets table."""
        with self.engine.begin() as conn:
            Base.metadata.drop_all(conn)

    def get_assets(self) -> list[Asset]:
        """Get all the assets in the table."""
        return list(self.session.execute(select(Asset)).scalars().fetchall())

    def get_asset_models(
        self,
        tickers: tuple[str, ...] | None = None,
    ) -> list[AssetModel]:
        """Get all the assets in the table."""
        if tickers:
            return list(
                self.session.execute(select(Asset).filter(Asset.ticker.in_(tickers)))
                .scalars()
                .fetchall()
            )
        return [AssetModel(**a.to_dict()) for a in self.get_assets()]

    def get_tickers(self) -> list[str]:
        """Get all the tickers in the assets table."""
        return list(self.session.execute(select(Asset.ticker)).scalars().fetchall())

    def get_assets_df(
        self,
        tickers: tuple[str, ...] | None = None,
    ) -> pd.DataFrame:
        """Get all the tickers in the assets table."""
        query = (
            f"SELECT * FROM {self.TABLE_NAME} WHERE ticker IN :tickers;"
            if tickers
            else f"SELECT * FROM {self.TABLE_NAME};"
        )
        with self.engine.begin() as conn:
            return pd.read_sql_query(sql=query, con=conn, params={"tickers": tickers})

    def get_number_of_shares(
        self,
        tickers: tuple[str, ...] | None = None,
    ) -> pd.DataFrame:
        """Get all the tickers in the assets table."""
        query = (
            f"SELECT ticker, number_of_shares FROM {self.TABLE_NAME} WHERE ticker IN :tickers;"
            if tickers
            else f"SELECT ticker, number_of_shares FROM {self.TABLE_NAME};"
        )
        with self.engine.begin() as conn:
            return pd.read_sql_query(sql=query, con=conn, params={"tickers": tickers})

    def write_assets(
        self,
        asset_models: list[AssetModel],
        updated_by: str | None = None,
        autocommit: bool = True,
    ) -> None:
        """Write assets in the database."""
        assets = [
            Asset(
                updated_by=updated_by,
                **asset_model.dict(exclude_none=True, exclude={"symbol"}),
            )
            for asset_model in asset_models
        ]
        self.session.add_all(assets)
        if autocommit:
            self.session.commit()
            log.info(f"Added {len(assets)} assets.")
