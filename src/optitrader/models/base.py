"""Config base model."""

from pydantic import BaseModel, Extra


class CustomBaseModel(BaseModel):
    """Custom base model with additional config and settings."""

    class Config:
        """Configuration."""

        extra = Extra.forbid
