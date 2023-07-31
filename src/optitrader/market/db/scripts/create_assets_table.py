"""Create the assets table."""
import logging
import os

from tqdm import tqdm

from optitrader.market.db.database import MarketDB
from optitrader.market.market_data import MarketData

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main(db: MarketDB, md: MarketData) -> None:
    """Run script function."""
    file_path = os.path.relpath(__file__)
    db.create_tables()
    univ_tickers = md.get_tradable_tickers()
    tickers_in_table = db.get_tickers()
    tickers = tuple(set(univ_tickers).difference(set(tickers_in_table)))
    chunk_size = 50
    log.info(f"Total to write: {len(tickers)} tickers")
    for chunk in tqdm(range(0, len(tickers), chunk_size)):
        tickers_bucket = tickers[chunk : chunk + chunk_size]
        log.info(f"Getting {len(tickers_bucket)} tickers:")
        asset_models = md.get_assets(tickers=tickers_bucket)
        asset_models = [a for a in asset_models if a.ticker not in tickers_in_table]
        log.info(f"Writing {len(asset_models)} tickers:")
        try:
            db.write_assets(asset_models=asset_models, updated_by=file_path)
        except Exception as exc:
            log.warning(exc)
            db.session.rollback()


if __name__ == "__main__":
    main(db=MarketDB(), md=MarketData(use_db=False))  # pragma: no cover
