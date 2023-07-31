"""Streamlit homepage."""
import streamlit as st

from optitrader.app import Page, session


def main() -> None:
    """Run dashboard."""
    page = Page(name="optitrader dashboard")
    page.display_title_and_description(
        description="""
        In this dashboard you can configure your optimal portfolio using several parameters.\n
        You can select the stocks that the solver should take into consideration when choosing the _investment universe_,
        then you can add and configure _objectives_ and _constraints_ for the optimization problem.\n
        Once you compute the optimal portfolio, analyze the solution obtained and
        head to the _backtester_ page to see how your strategy would've performed historically.\n
        """
    )
    col1, col2 = st.columns(2)
    with col1:
        session.set_universe_name()
        session.set_objective_names()
    with col2:
        session.set_start_date()
        session.set_constraint_names()
    session.run_optimization()
    session.invest_in_optimal_portfolio()
    session.display_solution()
    with st.sidebar:
        st.subheader("⚙️ Configure Optimization")
        session.set_objectives()
        session.set_constraints()
    if session._opt_ptf:
        session.display_news()
    page.display_code_sidebar()
