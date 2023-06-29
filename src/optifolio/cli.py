"""optifolio CLI."""

import subprocess

import typer

app = typer.Typer()


@app.command()
def say(message: str = "") -> None:
    """Say a message."""
    typer.echo(message)


@app.command()
def dashboard(port: int = 8000) -> None:
    """Open the streamlit dashboard."""
    subprocess.run(["poe", "app", "--port", str(port)])
    typer.launch(url="http://localhost:8000/")
