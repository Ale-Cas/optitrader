"""Update the number of shares in the assets table."""
import logging
import os

from optitrader.market.db.database import MarketDB
from optitrader.market.market_data import MarketData

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def main(db: MarketDB, md: MarketData) -> None:
    """Run script function."""
    file_path = os.path.relpath(__file__)
    db.create_tables()
    tickers_in_table = db.get_tickers()[500:550]
    shares = md.get_total_number_of_shares(tuple(tickers_in_table))
    df = db.update_number_of_shares(multi_number_of_shares=shares, updated_by=file_path)
    log.debug(df)


if __name__ == "__main__":
    main(db=MarketDB(), md=MarketData(use_db=False))  # pragma: no cover
