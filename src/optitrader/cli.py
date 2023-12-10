"""optitrader CLI."""

import subprocess

import typer

app = typer.Typer()


@app.command()
def say(message: str = "") -> None:
    """Say a message."""
    typer.echo(message)


@app.command()
def dashboard(port: int = 8000, launch: bool = True, timeout: int = 3) -> None:
    """Open the streamlit dashboard."""
    subprocess.run(["poe", "app", "--port", str(port)], timeout=timeout, check=True)
    if launch:
        typer.launch(url=f"http://localhost:{port}/")
