"""Module for loading settings and configurations from .env using pydantic."""
from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Settings and configurations.

    You can provide in the .env file either the Alpaca Trading API or Broker API keys.
    See more here:
    - [Trading API](https://alpaca.markets/docs/trading/getting_started/#creating-an-alpaca-account-and-finding-your-api-keys)
    - [Broker API](https://alpaca.markets/docs/broker/get-started/#api-keys)
    """

    # ALPACA SETTINGS
    ALPACA_TRADING_API_KEY: str | None = None
    ALPACA_TRADING_API_SECRET: str | None = None
    ALPACA_BROKER_API_KEY: str | None = None
    ALPACA_BROKER_API_SECRET: str | None = None

    # FINNHUB
    FINHUB_API_KEY: str | None = None

    # OPTIMIZATION SETTINGS
    # this means that if the portfolio's weights sum to 0.99 instead of 1 is accepted
    SUM_WEIGHTS_TOLERANCE: float = 1e-2

    # DB SETTINGS
    DB_URI_MARKET: str = "sqlite:///market.db"  # prod
    DB_URI_TEST: str = "sqlite:///test.db"  # test

    class Config:
        """Configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def is_trading(self) -> bool:
        """If the settings are for the trading keys."""
        return bool(self.ALPACA_TRADING_API_KEY or self.ALPACA_TRADING_API_SECRET)

    @property
    def is_broker(self) -> bool:
        """If the settings are for the broker keys."""
        return bool(self.ALPACA_BROKER_API_KEY or self.ALPACA_BROKER_API_SECRET)


SETTINGS = Settings()
