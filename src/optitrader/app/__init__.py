"""Init."""

from optitrader.app.page import Page
from optitrader.app.session_manager import SessionManager

session = SessionManager()
__all__ = [
    "session",
    "Page",
]
