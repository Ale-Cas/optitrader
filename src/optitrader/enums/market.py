"""All market data related Enums."""
from optitrader.enums import IterEnum


class DataProvider(IterEnum):
    """Supported data providers for market data."""

    ALPACA = "ALPACA"
    YAHOO = "YAHOO"


class BarsField(IterEnum):
    """Possile fields in the bars from the data provider."""

    OPEN = "open"
    HIGH = "high"
    LOW = "low"
    CLOSE = "close"
    VOLUME = "volume"


class UniverseName(IterEnum):
    """Supported universe names."""

    FAANG = "FAANG Stocks (Facebook, Apple, Amazon, Google & Netflix)"
    POPULAR_STOCKS = "Most Popular Stocks"
    NASDAQ = "NASDAQ 100"
    SP500 = "Standard & Poor 500"


class IncomeStatementItem(IterEnum):
    """
    Supported income statement fields.

    See https://finance.yahoo.com/quote/AAPL/financials?p=AAPL
    """

    REVENUE = "TotalRevenue"
    # -
    COST = "CostOfRevenue"
    # =
    GROSS_PROFIT = "GrossProfit"
    # -
    OPERATING_EXPENSE = "OperatingExpense"
    # =
    OPERATING_INCOME = "OperatingIncome"

    # After taxes and other expenses
    NET_INCOME = "NetIncome"
    EBIT = "EBIT"
    # EBITDA = "EBITDA"
    EBITDA = "NormalizedEBITDA"


class BalanceSheetItem(IterEnum):
    """
    Supported balance sheet fields.

    See https://finance.yahoo.com/quote/AAPL/financials?p=AAPL
    """

    ASSETS = "TotalAssets"
    LIABILITIES = "TotalLiabilitiesNetMinorityInterest"
    DEBT = "TotalDebt"
    WORKING_CAPITAL = "WorkingCapital"


class CashFlowItem(IterEnum):
    """
    Supported cash flow fields.

    See https://finance.yahoo.com/quote/AAPL/financials?p=AAPL
    """

    FREE = "FreeCashFlow"
    OPERATING = "OperatingCashFlow"
    INVESTING = "InvestingCashFlow"
    FINANCING = "FinancingCashFlow"
