"""Test optifolio REST API."""

import json

import httpx
import pytest
from fastapi.testclient import TestClient

from optifolio.api import app
from optifolio.config import SETTINGS
from optifolio.models import OptimizationRequest, OptimizationResponse

client = TestClient(app)
_tollerance = SETTINGS.SUM_WEIGHTS_TOLERANCE


@pytest.mark.timeout(10)
def test_read_root() -> None:
    """Test that reading the root is successful."""
    response = client.get("/")
    assert httpx.codes.is_success(response.status_code)


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
