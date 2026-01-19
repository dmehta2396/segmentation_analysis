"""
Tab layouts for dashboard
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def create_tabs_layout():
    """Create tabbed interface for different analysis views."""
    
    return dbc.Tabs([
        dbc.Tab(
            label="Overview",
            tab_id="tab-overview",
            children=[
                html.Div(id='overview-content', className='p-3')
            ]
        ),
        dbc.Tab(
            label="Product Analysis",
            tab_id="tab-products",
            children=[
                html.Div(id='product-content', className='p-3')
            ]
        ),
        dbc.Tab(
            label="Cohort Analysis",
            tab_id="tab-cohorts",
            children=[
                html.Div(id='cohort-content', className='p-3')
            ]
        ),
        dbc.Tab(
            label="Risk Dashboard",
            tab_id="tab-risk",
            children=[
                html.Div(id='risk-content', className='p-3')
            ]
        ),
        dbc.Tab(
            label="Entity Search",
            tab_id="tab-entity",
            children=[
                html.Div(id='entity-content', className='p-3')
            ]
        ),
    ], id="analysis-tabs", active_tab="tab-overview")