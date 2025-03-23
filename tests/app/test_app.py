"""Test running the streamlit app."""

import pytest

from optitrader.app import about, account, backtester, explore, home


@pytest.mark.timeout(20)
def test_run_pages_main() -> None:
    """Run pages main function."""
    about.main()
    account.main()
    backtester.main()
    explore.main()
    home.main()
