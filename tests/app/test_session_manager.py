"""Test session manager suite."""
from unittest.mock import MagicMock, Mock, call

import pytest
import streamlit as st
from pandas import Timestamp

from optifolio import MarketData, Optifolio, Portfolio
from optifolio.app.session_manager import SessionManager
from optifolio.enums import ConstraintName, ObjectiveName, RebalanceFrequency, UniverseName


@pytest.fixture()
def session_manager() -> SessionManager:
    """Session manager."""
    return SessionManager()


def test_set_api_keys(
    session_manager: SessionManager,
) -> None:
    """Test for the set_api_keys method of SessionManager class."""
    st.text_input = Mock(return_value="API_KEY")
    st.form_submit_button = Mock(return_value=True)

    session_manager.set_api_keys()

    assert isinstance(session_manager.market_data, MarketData)
    assert session_manager.market_data._trading_key == "API_KEY"


def test_set_universe_name(
    session_manager: SessionManager,
) -> None:
    """Test for the set_universe_name method of SessionManager class."""
    st.selectbox = Mock(return_value=UniverseName.FAANG.value)

    session_manager.set_universe_name()

    assert session_manager.universe_name == UniverseName.FAANG


def test_set_start_date(session_manager: SessionManager, test_start_date: Timestamp) -> None:
    """Test for the set_start_date method of SessionManager class."""
    st.date_input = Mock(return_value=test_start_date)

    session_manager.set_start_date()

    assert session_manager.start_date == test_start_date


def test_set_objective_names(
    session_manager: SessionManager,
) -> None:
    """Test for the set_objective_names method of SessionManager class."""
    st.multiselect = Mock(return_value=[ObjectiveName.CVAR.value])

    session_manager.set_objective_names()

    assert session_manager.objective_names == [ObjectiveName.CVAR]


def test_set_objectives(
    session_manager: SessionManager,
) -> None:
    """Test for the set_objective_names method of SessionManager class."""
    name = ObjectiveName.CVAR.value
    st.multiselect = Mock(return_value=[name])
    st.number_input = Mock(return_value=1)

    session_manager.set_objectives()

    objs = session_manager.obj_map.objectives
    assert len(objs) == 1
    assert objs[0].name == name


def test_set_constraint_names(
    session_manager: SessionManager,
) -> None:
    """Test for the set_constraint_names method of SessionManager class."""
    st.multiselect = Mock(return_value=[ConstraintName.SUM_TO_ONE.value])

    session_manager.set_constraint_names()

    assert session_manager.constraint_names == [ConstraintName.SUM_TO_ONE]


def test_set_rebalance_frequency(
    session_manager: SessionManager,
) -> None:
    """Test for the set_rebalance_frequency method of SessionManager class."""
    st.selectbox = Mock(return_value=RebalanceFrequency.MONTHLY.name)

    session_manager.set_rebalance_frequency()

    assert session_manager.rebalance_frequency == RebalanceFrequency.MONTHLY


def test_get_optifolio(
    session_manager: SessionManager,
) -> None:
    """Test for the get_optifolio method of SessionManager class."""
    session_manager.market_data = MarketData()

    optifolio = session_manager.get_optifolio()

    assert isinstance(optifolio, Optifolio)
    assert optifolio.investment_universe.name == session_manager.universe_name
    assert optifolio.market_data == session_manager.market_data


def test_run_optimization(
    session_manager: SessionManager,
) -> None:
    """Test for the run_optimization method of SessionManager class."""
    st.button = Mock(return_value=True)
    st.spinner = MagicMock()
    st.dataframe = MagicMock()

    # Setup the objectives:
    name = ObjectiveName.CVAR.value
    st.multiselect = Mock(return_value=[name])
    st.number_input = Mock(return_value=1)
    session_manager.set_objectives()
    objs = session_manager.obj_map.objectives
    assert len(objs) == 1
    assert objs[0].name == name
    # (might need refactor with hipothesis)

    session_manager._opt_ptf = None  # manually make sure the cache is not there
    session_manager.run_optimization()

    st.button.assert_called_once_with(label="COMPUTE OPTIMAL PORTFOLIO")
    assert len(st.spinner.mock_calls) == 3  # noqa: PLR2004 # enter, exit and description
    _opt_ptf = session_manager._opt_ptf
    assert _opt_ptf is not None
    assert isinstance(_opt_ptf, Portfolio)  # type: ignore


def test_display_optifolio_problem(session_manager: SessionManager) -> None:
    """Test for the display_optifolio_problem method of SessionManager class."""
    st.sidebar = MagicMock()
    st.expander = MagicMock()
    st.write = Mock()

    session_manager.universe_name = UniverseName.FAANG
    session_manager.start_date = Timestamp("2022-01-01")
    session_manager.objective_names = [ObjectiveName.CVAR]
    session_manager.constraint_names = [ConstraintName.SUM_TO_ONE]

    session_manager.display_optifolio_problem()
    st.sidebar.assert_has_calls([call.__enter__(), call.__exit__(None, None, None)])
    st.expander.assert_has_calls(
        [
            call("Investment Universe", expanded=True),
            call().__enter__(),
            call().__exit__(None, None, None),
            call("Start Date", expanded=True),
            call().__enter__(),
            call().__exit__(None, None, None),
            call("Objectives", expanded=True),
            call().__enter__(),
            call().__exit__(None, None, None),
            call("Constraints", expanded=True),
            call().__enter__(),
            call().__exit__(None, None, None),
        ]
    )
    _write_mock_calls = st.write.mock_calls
    assert _write_mock_calls[1] == call("2022-01-01")
    assert _write_mock_calls[2] == call(ObjectiveName.CVAR)
    assert _write_mock_calls[3] == call(ConstraintName.SUM_TO_ONE)


def test_display_alpaca_account_sidebar(session_manager: SessionManager) -> None:
    """Test for the display_alpaca_account_sidebar method of SessionManager class."""
    st.sidebar = MagicMock()
    st.write = Mock()
    st.markdown = Mock()

    session_manager.display_alpaca_account_sidebar()

    st.sidebar.assert_has_calls([call.__enter__(), call.__exit__(None, None, None)])
    st.write.assert_called_once_with(
        "The default data come from my personal Alpaca trading sandbox API keys."
    )
    assert len(st.markdown.mock_calls) == 1


def test_display_financials(session_manager: SessionManager) -> None:
    """Test for the display_financials method of SessionManager class."""
    st.plotly_chart = MagicMock()
    st.markdown = Mock()

    session_manager.display_financials()

    assert len(st.markdown.mock_calls) == 1
    assert len(st.plotly_chart.mock_calls) == 3  # noqa: PLR2004 # 3 statements
