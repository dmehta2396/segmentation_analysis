"""
Main content layout
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def create_main_content_layout(base_month, current_month, metric_display,
                               comparison_chart, sankey, summary_chart, 
                               heatmap, summary_table, matrix_table):
    """Create main content area layout."""
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3(f"Analysis: {base_month} → {current_month}", 
                       className="mb-3",
                       style={'color': '#2E86AB'})
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5(f"{metric_display} - Base vs Current")),
                    dbc.CardBody([
                        dcc.Graph(figure=comparison_chart, config={'displayModeBar': False})
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5(f"{metric_display} - Segment Flow (Sankey)")),
                    dbc.CardBody([
                        dcc.Graph(figure=sankey, config={'displayModeBar': False})
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5(f"{metric_display} - Movement Breakdown")),
                    dbc.CardBody([
                        dcc.Graph(figure=summary_chart, config={'displayModeBar': False})
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5(f"{metric_display} - Movement Matrix")),
                    dbc.CardBody([
                        dcc.Graph(figure=heatmap, config={'displayModeBar': False})
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5(f"{metric_display} - Summary Table")),
                    dbc.CardBody([
                        summary_table
                    ], style={'overflowX': 'auto'})
                ])
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5(f"{metric_display} - Matrix Table")),
                    dbc.CardBody([
                        matrix_table
                    ], style={'overflowX': 'auto'})
                ])
            ], width=6)
        ])
    ], fluid=True)