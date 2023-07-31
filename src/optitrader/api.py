"""optitrader REST API."""

import logging
from collections import OrderedDict

import coloredlogs
import pandas as pd
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse

from optitrader.market.investment_universe import InvestmentUniverse
from optitrader.market.market_data import MarketData
from optitrader.models import OptimizationRequest, OptimizationResponse
from optitrader.optimization.solver import Solver

app = FastAPI(title="optitrader API")


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


@app.post("/optimization")
def compute_optimal_portfolio(
    request_body: OptimizationRequest,
) -> OptimizationResponse:
    """Compute the optimal portfolio."""
    market = MarketData()
    if not (request_body.tickers or request_body.universe_name):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="You must provide either tickers or universe name",
        )
    opt_ptf = Solver(
        returns=market.get_total_returns(
            tickers=InvestmentUniverse(name=request_body.universe_name).tickers
            if request_body.universe_name
            else request_body.tickers
            if request_body.tickers  # for mypy
            else (),
            start_date=pd.Timestamp(request_body.start_date),
            end_date=pd.Timestamp(request_body.end_date),
        ),
        constraints=[con.to_ptf_constraint() for con in request_body.constraints],
        objectives=[obj.to_ptf_objective() for obj in request_body.objectives],
    ).solve(
        weights_tolerance=request_body.weights_tolerance,
    )
    return OptimizationResponse(
        weights=opt_ptf.get_non_zero_weights().to_dict(OrderedDict),
        objective_values=opt_ptf.objective_values,
    )
