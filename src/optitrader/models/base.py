"""Config base model."""

from pydantic import BaseModel, ConfigDict


class CustomBaseModel(BaseModel):
    """Custom base model with additional config and settings."""

    model_config = ConfigDict(extra="forbid")
