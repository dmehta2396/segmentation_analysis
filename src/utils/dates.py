"""
Date utility functions
"""

import time
from functools import wraps


def timer(func):
    """Decorator to time function execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        print(f"\n{'='*60}")
        print(f"FUNCTION: {func.__name__}")
        print(f"{'='*60}")
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"⏱️  {func.__name__} completed in {duration:.2f} seconds")
        print(f"{'='*60}")
        
        return result
    return wrapper


def get_ttm_months(month: int, num_months: int = 12) -> list:
    """
    Get list of months for TTM (Trailing Twelve Months) period.
    
    Args:
        month: YYYYMM format (e.g., 202408)
        num_months: Number of months to go back (default 12)
        
    Returns:
        List of months in YYYYMM format
    """
    year = month // 100
    month_num = month % 100
    
    months = []
    for i in range(num_months):
        m = month_num - i
        y = year
        
        while m <= 0:
            m += 12
            y -= 1
        
        months.append(y * 100 + m)
    
    return sorted(months)