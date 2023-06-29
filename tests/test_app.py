"""Test running the streamlit app."""
import subprocess
from time import sleep

import pytest

from optifolio import app


@pytest.mark.timeout(2)
def test_run_streamlit() -> None:
    """Run the streamlit app at examples/streamlit_app.py on port 8599."""
    cmd = ["poe", "app", "--port", "8503"]
    p = subprocess.Popen(cmd)
    try:
        sleep(1)
    finally:
        assert not p.stderr
        p.kill()


@pytest.mark.timeout(1)
def test_run_app_main(capsys: pytest.CaptureFixture) -> None:
    """Test the main function from the app file."""
    app.main()
    # streamlit will output an error since the main function is not meant to be executed this way
    assert "Streamlit" in capsys.readouterr().err
