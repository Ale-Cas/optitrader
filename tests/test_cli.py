"""Test optifolio CLI."""

from typer.testing import CliRunner

from optifolio.cli import app

runner = CliRunner()


def test_say() -> None:
    """Test that the say command works as expected."""
    message = "Test"
    result = runner.invoke(app, ["say", "--message", message])
    assert result.exit_code == 0
    assert message in result.stdout


def test_dashboard() -> None:
    """Test that the dashboard command works as expected."""
    result = runner.invoke(app, "dashboard")
    assert result.exit_code == 0
