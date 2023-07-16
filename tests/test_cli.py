"""Test optifolio CLI."""

import subprocess
from unittest.mock import MagicMock, Mock

import pytest
import typer
from typer.testing import CliRunner

from optifolio.cli import app, dashboard

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
    assert isinstance(result.exception, subprocess.TimeoutExpired)


@pytest.mark.timeout(2)
def test_dashboard_no_launch() -> None:
    """Test that the dashboard command works as expected."""
    result = runner.invoke(app, ["dashboard", "--no-launch", "--timeout=1"])
    assert result.exit_code == 1
    assert isinstance(result.exception, subprocess.TimeoutExpired)


@pytest.mark.timeout(3)
def test_dashboard_launch() -> None:
    """Test that the dashboard command works as expected."""
    app.command = MagicMock()  # type: ignore
    subprocess.run = Mock()
    typer.launch = Mock()
    dashboard(launch=True, port=1234)
    subprocess.run.assert_called_once()
    typer.launch.assert_called_once()
    typer.launch.assert_called_once_with(url="http://localhost:1234/")
