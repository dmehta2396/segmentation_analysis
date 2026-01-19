"""
Sidebar layout component
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def create_sidebar(base_month, available_months):
    """Create sidebar with controls."""
    
    comparison_month_options = [
        {'label': str(m), 'value': m} 
        for m in available_months
    ]
    
    default_current = available_months[-1] if available_months else None
    
    return dbc.Card([
        dbc.CardBody([
            html.H5("Analysis Parameters", className="card-title mb-4"),
            
            html.Label("Base Month (Fixed):", style={'fontWeight': 'bold'}),
            html.H6(f"{base_month}", 
                   style={'color': '#5B8C5A', 'marginBottom': '20px'}),
            
            html.Label("Select Comparison Month:", 
                      style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            dcc.Dropdown(
                id='month-selector',
                options=comparison_month_options,
                value=default_current,
                clearable=False,
                style={'marginBottom': '20px'}
            ),
            
            html.Label("Select Metric:", 
                      style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            dcc.Dropdown(
                id='metric-selector',
                options=[{'label': 'Count', 'value': 'count'}],
                value='count',
                clearable=False,
                style={'marginBottom': '20px'}
            ),
            
            dbc.Button("Generate Analysis", 
                      id='submit-button', 
                      color="primary", 
                      className="w-100 mb-3",
                      size='lg'),
            
            html.Hr(),
            
            html.H6("Advanced Features", className="mt-3 mb-3"),
            
            dbc.Button("Export to Excel", 
                      id='export-excel-button',
                      color="success",
                      className="w-100 mb-2",
                      size='sm',
                      disabled=True),
            
            dbc.Button("Generate Risk Report", 
                      id='export-risk-button',
                      color="warning",
                      className="w-100 mb-2",
                      size='sm',
                      disabled=True),
            
            html.Hr(),
            
            html.Label("Entity Search:", style={'fontWeight': 'bold', 'marginTop': '10px'}),
            dcc.Input(
                id='entity-search-input',
                type='text',
                placeholder='Enter Entity ID',
                className='form-control mb-2',
                style={'width': '100%'}
            ),
            dbc.Button("Search Entity", 
                      id='search-entity-button',
                      color="info",
                      className="w-100",
                      size='sm',
                      disabled=True)
        ])
    ], style={'position': 'sticky', 'top': '20px'})