"""Test optifolio CLI."""

from subprocess import TimeoutExpired

import pytest
from typer.testing import CliRunner

from optifolio.cli import app

runner = CliRunner()


@pytest.mark.timeout(1)
def test_say() -> None:
    """Test that the say command works as expected."""
    message = "Test"
    result = runner.invoke(app, ["say", "--message", message])
    assert result.exit_code == 0
    assert message in result.stdout


@pytest.mark.timeout(2)
def test_dashboard() -> None:
    """Test that the dashboard command works as expected."""
    result = runner.invoke(app, ["dashboard", "--launch", "--timeout=1"])
    assert result.exit_code == 1
    assert isinstance(result.exception, TimeoutExpired)


@pytest.mark.timeout(2)
def test_dashboard_no_launch() -> None:
    """Test that the dashboard command works as expected."""
    result = runner.invoke(app, ["dashboard", "--no-launch", "--timeout=1"])
    assert result.exit_code == 1
    assert isinstance(result.exception, TimeoutExpired)
