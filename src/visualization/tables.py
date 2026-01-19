"""
Table formatting functions
"""

import dash_bootstrap_components as dbc


def create_summary_table(df):
    """Create formatted HTML table."""
    df_display = df.copy()
    numeric_cols = df_display.select_dtypes(include=['float64', 'int64']).columns
    
    for col in numeric_cols:
        df_display[col] = df_display[col].apply(lambda x: f'{x:,.2f}')
    
    return dbc.Table.from_dataframe(
        df_display, 
        striped=True, 
        bordered=True, 
        hover=True,
        responsive=True,
        size='sm',
        style={'fontSize': '0.9rem'}
    )