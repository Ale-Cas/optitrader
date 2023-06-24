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

    class Config:
        """Configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"


SETTINGS = Settings()
