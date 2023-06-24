"""optifolio REST API."""

import logging

import coloredlogs
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()


@app.on_event("startup")
def startup_event() -> None:
    """Run API startup events."""
    # Remove all handlers associated with the root logger object.
    for handler in logging.root.handlers:
        logging.root.removeHandler(handler)
    # Add coloredlogs' coloured StreamHandler to the root logger.
    coloredlogs.install()


@app.get("/")
def reroute_to_docs() -> RedirectResponse:
    """Automatically redirect homepage to docs."""
    return RedirectResponse(url="/docs")
