"""Local SQL storage of assets table."""
import logging

import pandas as pd
from sqlalchemy import create_engine, select
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session, sessionmaker

from optifolio.config import SETTINGS
from optifolio.market.db.models import Asset, Base
from optifolio.models.asset import AssetModel

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class MarketDB:
    """Class to handle interactions with sqlite market.db database."""

    def __init__(self, uri: str = SETTINGS.DB_URI_MARKET) -> None:
        """Initialize the market database object."""
        self.engine = create_engine(uri, connect_args={"check_same_thread": False})
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

    def get_assets(
        self,
        tickers: tuple[str, ...] | None = None,
    ) -> list[Asset]:
        """Get all the assets in the table."""
        if tickers:
            return list(
                self.session.execute(select(Asset).filter(Asset.ticker.in_(tickers)))
                .scalars()
                .fetchall()
            )
        return list(self.session.execute(select(Asset)).scalars().fetchall())

    def get_asset(self, ticker: str) -> AssetModel:
        """Get the asset model from the table by ticker."""
        return AssetModel.from_orm(
            list(
                self.session.execute(select(Asset).where(Asset.ticker == ticker))
                .scalars()
                .fetchall()
            )[0]
        )

    def get_asset_models(
        self,
        tickers: tuple[str, ...] | None = None,
    ) -> list[AssetModel]:
        """Get all the assets in the table."""
        return [AssetModel.from_orm(a) for a in self.get_assets(tickers)]

    def get_tickers(self) -> list[str]:
        """Get all the tickers in the assets table."""
        return list(self.session.execute(select(Asset.ticker)).scalars().fetchall())

    def get_assets_df(
        self,
        tickers: tuple[str, ...] | None = None,
    ) -> pd.DataFrame:
        """Get all the tickers in the assets table."""
        query = select(Asset).filter(Asset.ticker.in_(tickers)) if tickers else select(Asset)
        with self.engine.begin() as conn:
            return pd.read_sql_query(sql=query, con=conn)

    def get_number_of_shares(
        self,
        tickers: tuple[str, ...] | None = None,
    ) -> pd.DataFrame:
        """Get all the tickers in the assets table."""
        query = (
            select(Asset.ticker, Asset.number_of_shares).filter(Asset.ticker.in_(tickers))
            if tickers
            else select(Asset.ticker, Asset.number_of_shares)
        )
        with self.engine.begin() as conn:
            return pd.read_sql_query(sql=query, con=conn)

    def write_asset(
        self,
        asset_model: AssetModel,
        updated_by: str | None = None,
        autocommit: bool = True,
    ) -> None:
        """Write assets in the database."""
        asset = Asset(
            updated_by=updated_by,
            **asset_model.dict(exclude_none=True, exclude={"symbol"}),
        )
        self.session.add(asset)
        if autocommit:
            self.session.commit()
            log.info(f"Added {asset}.")

    def write_assets(
        self,
        asset_models: list[AssetModel],
        updated_by: str | None = None,
        autocommit: bool = True,
    ) -> None:
        """Write assets in the database."""
        for asset_model in asset_models:
            try:
                self.write_asset(asset_model, updated_by=updated_by, autocommit=autocommit)
            except DatabaseError as dberror:
                log.warning(f"{type(dberror)} for {asset_model.ticker}")
                log.warning(dberror)
                if autocommit:
                    self.session.rollback()
        log.info(f"Added {len(asset_models)} assets.")
