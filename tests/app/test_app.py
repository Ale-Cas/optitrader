"""Test running the streamlit app."""
import subprocess
from time import sleep

import pytest

from optitrader.app import about, account, backtester, explore, home


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


@pytest.mark.timeout(20)
def test_run_pages_main() -> None:
    """Run pages main function."""
    about.main()
    account.main()
    backtester.main()
    explore.main()
    home.main()
