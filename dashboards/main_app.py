"""
Main Dash application with advanced features
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
import time

from src.config.settings import DASHBOARD_HOST, DASHBOARD_PORT, DEBUG_MODE, SEGMENT_COLS
from src.data.loader import get_available_current_months, load_base_seg, load_metrics_glbl
from dashboards.layouts.sidebar import create_sidebar
from dashboards.layouts.tabs import create_tabs_layout
from dashboards.callbacks.snapshot_callbacks import register_snapshot_callbacks
from dashboards.callbacks.viz_callbacks import register_viz_callbacks
from dashboards.callbacks.advanced_callbacks import register_advanced_callbacks

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Segmentation Analysis Dashboard"

# Load static data once
print("\n" + "="*60)
print("DASHBOARD INITIALIZATION")
print("="*60)
init_start = time.time()

base_seg = load_base_seg()
metrics_glbl = load_metrics_glbl()
available_months = get_available_current_months()

base_month = base_seg[SEGMENT_COLS['month']].iloc[0]

print(f"\nBase month: {base_month}")
print(f"Available comparison months: {available_months}")

init_end = time.time()
print(f"⏱️  Initialization: {init_end - init_start:.2f} seconds")
print("="*60)

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Segmentation Analysis Dashboard", 
                   className="text-center mb-4 mt-4",
                   style={'color': '#2E86AB'})
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            create_sidebar(base_month, available_months)
        ], width=3),
        
        dbc.Col([
            html.Div(id='status-message', className='mb-3'),
            html.Div(id='export-status', className='mb-3'),
            create_tabs_layout()
        ], width=9)
    ]),
    
    dcc.Loading(
        id="loading",
        type="default",
        children=[
            html.Div(id='loading-output', style={'display': 'none'})
        ]
    ),
    
    # Stores
    dcc.Store(id='snapshot-data'),
    dcc.Store(id='current-month-store'),
    dcc.Store(id='analysis-complete', data=False)
    
], fluid=True, style={'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})

# Register callbacks
register_snapshot_callbacks(app, base_seg, metrics_glbl, base_month)
register_viz_callbacks(app, base_month)
register_advanced_callbacks(app, base_month)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("STARTING DASHBOARD SERVER")
    print(f"Open browser: http://localhost:{DASHBOARD_PORT}")
    print("="*60 + "\n")
    app.run_server(debug=DEBUG_MODE, host=DASHBOARD_HOST, port=DASHBOARD_PORT)