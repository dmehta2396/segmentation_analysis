"""
Formatting utility functions
"""


def format_number(value: float, decimals: int = 0) -> str:
    """Format number with comma separators."""
    if decimals == 0:
        return f"{value:,.0f}"
    return f"{value:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format percentage."""
    return f"{value:.{decimals}f}%"


def format_currency(value: float, symbol: str = "$") -> str:
    """Format currency."""
    return f"{symbol}{value:,.2f}"