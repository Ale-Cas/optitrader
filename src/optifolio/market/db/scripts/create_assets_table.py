"""Create the assets table."""
import os

from optifolio.enums.market import UniverseName
from optifolio.market.db.database import MarketDB
from optifolio.market.investment_universe import InvestmentUniverse
from optifolio.market.market_data import MarketData


def main() -> None:
    """Run script function."""
    file_path = os.path.relpath(__file__)
    db = MarketDB()
    univ_tickers = tuple(sorted(InvestmentUniverse(name=UniverseName.SP500).tickers)[80:120])
    db.create_tables()
    tickers_in_table = db.get_tickers()
    tickers = tuple(set(univ_tickers).difference(set(tickers_in_table)))
    asset_models = MarketData().get_assets(tickers=tickers)
    asset_models = [a for a in asset_models if a.ticker not in tickers_in_table]
    db.write_assets(asset_models=asset_models, updated_by=file_path)


if __name__ == "__main__":
    main()
