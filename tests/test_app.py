"""Test running the streamlit app."""
import subprocess
from time import sleep

import pytest


@pytest.mark.timeout(3)
def test_run_streamlit():
    """Run the streamlit app at examples/streamlit_app.py on port 8599."""
    cmd = ["poe", "app", "--port", "8503"]
    p = subprocess.Popen(cmd)
    try:
        sleep(2)
    finally:
        assert not p.errors
        assert not p.stderr
        p.kill()
