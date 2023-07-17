"""Local SQL storage of assets table."""
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from optifolio.market.db.models import Asset, Base
from optifolio.models.asset import AssetModel


class MarketDB:
    """Class to handle interactions with sqlite market.db database."""

    SQLALCHEMY_DATABASE_URL = "sqlite:///market.db"

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

    def get_tickers(self) -> list[str]:
        """Get all the tickers in the assets table."""
        return [str(a.ticker) for a in self.get_assets()]

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
