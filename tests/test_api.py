"""Test optitrader REST API."""

import json

import httpx
import pytest
from fastapi.testclient import TestClient

from optitrader.api import app
from optitrader.config import SETTINGS
from optitrader.models import OptimizationRequest, OptimizationResponse

client = TestClient(app, base_url="http://127.0.0.1/")
_tollerance = SETTINGS.SUM_WEIGHTS_TOLERANCE


@pytest.mark.timeout(1)
def test_read_root() -> None:
    """Test that reading the root is successful."""
    with TestClient(app) as client:
        response = client.get("/")
        assert response.history[0].status_code == httpx.codes.TEMPORARY_REDIRECT
        assert httpx.codes.is_success(response.status_code)
        assert "/docs" in str(response.url)


@pytest.mark.timeout(10)
def test_post_optimization(optimization_request: OptimizationRequest) -> None:
    """Test the post optimization endpoint."""
    response = client.post("/optimization", json=json.loads(optimization_request.json()))
    assert httpx.codes.is_success(response.status_code)
    response_model = OptimizationResponse(**response.json())
    assert response_model.objective_values[0].name == optimization_request.objectives[0].name
    weights = response_model.weights.values()
    assert sum(weights) - 1 <= _tollerance
    assert all(w >= _tollerance for w in weights)


@pytest.mark.timeout(1)
def test_post_optimization_invalid_body(optimization_request: OptimizationRequest) -> None:
    """Test the post optimization endpoint."""
    optimization_request.universe_name = None
    response = client.post("/optimization", json=json.loads(optimization_request.json()))
    assert httpx.codes.is_error(response.status_code)
    assert response.status_code == httpx.codes.UNPROCESSABLE_ENTITY


@pytest.mark.timeout(10)
@pytest.mark.vcr(ignore_localhost=True)
def test_post_optimization_with_fixed_dates(
    optimization_request_w_dates: OptimizationRequest,
) -> None:
    """Test the post optimization endpoint."""
    response = client.post("/optimization", json=json.loads(optimization_request_w_dates.json()))
    assert httpx.codes.is_success(response.status_code)
    response_model = OptimizationResponse(**response.json())
    assert (
        response_model.objective_values[0].name == optimization_request_w_dates.objectives[0].name
    )
    weights = response_model.weights.values()
    assert sum(weights) - 1 <= _tollerance
    assert all(w >= _tollerance for w in weights)
