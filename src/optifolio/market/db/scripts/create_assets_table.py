"""Create the assets table."""
import os

from tqdm import tqdm

from optifolio.market.db.database import MarketDB
from optifolio.market.market_data import MarketData


def main() -> None:
    """Run script function."""
    file_path = os.path.relpath(__file__)
    db = MarketDB()
    md = MarketData(use_db=False)
    univ_tickers = md.get_tradable_tickers()
    db.create_tables()
    tickers_in_table = db.get_tickers()
    tickers = tuple(set(univ_tickers).difference(set(tickers_in_table)))
    chunk_size = 50
    print(f"Total to write: {len(tickers)} tickers")
    for chunk in tqdm(range(0, len(tickers), chunk_size)):
        tickers_bucket = tickers[chunk : chunk + chunk_size]
        print(f"Getting {len(tickers_bucket)} tickers:")
        asset_models = md.get_assets(tickers=tickers_bucket)
        asset_models = [a for a in asset_models if a.ticker not in tickers_in_table]
        print(f"Writing {len(asset_models)} tickers:")
        try:
            db.write_assets(asset_models=asset_models, updated_by=file_path)
        except Exception as exc:
            print(exc)
            db.session.rollback()


if __name__ == "__main__":
    main()
