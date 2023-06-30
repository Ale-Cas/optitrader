"""Streamlit homepage."""  # noqa: N999

from optifolio.app import Page, session


def main() -> None:
    """Run dashboard."""
    page = Page(name="Optifolio dashboard")
    page.display_title_and_description(
        description="""
        In this dashboard you can configure your optimal portfolio using several parameters.
        You can select the stocks that the solver should take into consideration when choosing the _investment universe_,
        then you can add and configure _objectives_ and _constraints_ for the optimization problem.
        Once you compute the optimal portfolio, analyze the solution obtained and
        head to the _backtester_ page to see how your strategy would've performed historically.
        """
    )
    session.set_universe_name()
    session.set_objective_names()
    session.set_objectives()
    session.set_start_date()
    session.run_optimization()
    session.display_alpaca_account_sidebar()
    page.display_code_sidebar()


if __name__ == "__main__":
    main()
