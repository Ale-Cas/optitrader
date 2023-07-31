"""Add an asset to the assets table."""
import logging
import os

from optitrader.market.db.database import MarketDB
from optitrader.market.market_data import MarketData

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main(ticker: str, db: MarketDB, md: MarketData) -> None:
    """Run script function."""
    file_path = os.path.relpath(__file__)
    db.create_tables()
    tickers_in_table = db.get_tickers()
    if ticker not in tickers_in_table:
        asset_model = md.get_asset(ticker)
        log.debug(asset_model)
        db.write_asset(asset_model=asset_model, updated_by=file_path)


if __name__ == "__main__":
    main(ticker="WMT", db=MarketDB(), md=MarketData(use_db=False))  # pragma: no cover
