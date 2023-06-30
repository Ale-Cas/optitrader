"""Init."""

from optifolio.app.page import Page
from optifolio.app.session_manager import SessionManager

session = SessionManager()
__all__ = [
    "session",
    "Page",
]
