"""
Advanced feature callbacks
"""

import pandas as pd
from dash import Input, Output, State, html
import dash_bootstrap_components as dbc
from dash import dcc

from src.analysis.metrics import (
    calculate_product_mix,
    calculate_segment_product_matrix,
    calculate_entity_metrics
)
from src.analysis.cohort import (
    identify_segment_cohorts,
    calculate_cohort_revenue_metrics
)
from src.analysis.risk import (
    calculate_churn_risk_score,
    identify_at_risk_segments
)
from src.analysis.summary import generate_summary_view
from src.analysis.matrix import generate_movement_matrix
from src.visualization.advanced_charts import (
    create_product_mix_pie,
    create_segment_product_heatmap,
    create_cohort_retention_chart,
    create_cohort_revenue_waterfall,
    create_risk_gauge,
    create_risk_scatter,
    create_segment_risk_bars,
    create_entity_journey_timeline
)
from src.visualization.tables import create_summary_table
from src.utils.export import export_to_excel, export_risk_report, export_cohort_analysis


def register_advanced_callbacks(app, base_month):
    """Register callbacks for advanced features."""
    
    # Enable/disable buttons
    @app.callback(
        [Output('export-excel-button', 'disabled'),
         Output('export-risk-button', 'disabled'),
         Output('search-entity-button', 'disabled')],
        [Input('snapshot-data', 'data')]
    )
    def enable_buttons(snapshot_data):
        """Enable buttons when snapshot is generated."""
        disabled = snapshot_data is None
        return disabled, disabled, disabled
    
    
    # Product Analysis Tab
    @app.callback(
        Output('product-content', 'children'),
        [Input('analysis-tabs', 'active_tab'),
         Input('snapshot-data', 'data')]
    )
    def update_product_tab(active_tab, snapshot_dict):
        """Update product analysis tab."""
        
        if active_tab != 'tab-products' or snapshot_dict is None:
            return html.Div()
        
        snapshot = pd.DataFrame(snapshot_dict)
        
        # Calculate product mix
        product_mix = calculate_product_mix(snapshot)
        
        # Calculate segment-product matrix
        seg_product_matrix = calculate_segment_product_matrix(snapshot)
        
        # Create visualizations
        pie_chart = create_product_mix_pie(product_mix, "Revenue")
        heatmap = create_segment_product_heatmap(seg_product_matrix)
        
        # Create table
        product_table = create_summary_table(product_mix)
        
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H3("Product Analysis", className="mb-4")
                ])
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Product Revenue Mix")),
                        dbc.CardBody([
                            dcc.Graph(figure=pie_chart, config={'displayModeBar': False})
                        ])
                    ])
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Product Mix Table")),
                        dbc.CardBody([
                            product_table
                        ])
                    ])
                ], width=6)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Product Revenue by Segment")),
                        dbc.CardBody([
                            dcc.Graph(figure=heatmap, config={'displayModeBar': False})
                        ])
                    ])
                ], width=12)
            ])
        ], fluid=True)
    
    
    # Cohort Analysis Tab
    @app.callback(
        Output('cohort-content', 'children'),
        [Input('analysis-tabs', 'active_tab'),
         Input('snapshot-data', 'data')]
    )
    def update_cohort_tab(active_tab, snapshot_dict):
        """Update cohort analysis tab."""
        
        if active_tab != 'tab-cohorts' or snapshot_dict is None:
            return html.Div()
        
        snapshot = pd.DataFrame(snapshot_dict)
        
        # Calculate cohort metrics
        cohort_df = identify_segment_cohorts(snapshot)
        cohort_rev_df = calculate_cohort_revenue_metrics(snapshot)
        
        # Create visualizations
        retention_chart = create_cohort_retention_chart(cohort_df)
        waterfall_chart = create_cohort_revenue_waterfall(cohort_rev_df)
        
        # Create tables
        cohort_table = create_summary_table(cohort_df)
        revenue_table = create_summary_table(cohort_rev_df)
        
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H3("Cohort Analysis", className="mb-4"),
                    html.P("Analyze entity behavior grouped by their base segment (cohort)")
                ])
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Cohort Retention & Churn Rates")),
                        dbc.CardBody([
                            dcc.Graph(figure=retention_chart, config={'displayModeBar': False})
                        ])
                    ])
                ], width=12)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Cohort Revenue Changes")),
                        dbc.CardBody([
                            dcc.Graph(figure=waterfall_chart, config={'displayModeBar': False})
                        ])
                    ])
                ], width=12)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Cohort Movement Details")),
                        dbc.CardBody([
                            cohort_table
                        ])
                    ])
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Cohort Revenue Details")),
                        dbc.CardBody([
                            revenue_table
                        ])
                    ])
                ], width=6)
            ])
        ], fluid=True)
    
    
    # Risk Dashboard Tab
    @app.callback(
        Output('risk-content', 'children'),
        [Input('analysis-tabs', 'active_tab'),
         Input('snapshot-data', 'data')]
    )
    def update_risk_tab(active_tab, snapshot_dict):
        """Update risk dashboard tab."""
        
        if active_tab != 'tab-risk' or snapshot_dict is None:
            return html.Div()
        
        snapshot = pd.DataFrame(snapshot_dict)
        
        # Calculate risk scores
        entity_risk_df = calculate_churn_risk_score(snapshot)
        segment_risk_df = identify_at_risk_segments(snapshot)
        
        # Calculate summary metrics
        high_risk_count = len(entity_risk_df[entity_risk_df['risk_level'] == 'High'])
        avg_risk_score = entity_risk_df['risk_score'].mean()
        high_risk_segments = len(segment_risk_df[segment_risk_df['Risk Level'] == 'High'])
        
        # Create visualizations
        avg_gauge = create_risk_gauge(avg_risk_score, "Average Risk Score")
        scatter_chart = create_risk_scatter(entity_risk_df)
        segment_bars = create_segment_risk_bars(segment_risk_df)
        
        # Create tables
        top_risk_table = create_summary_table(entity_risk_df.head(20))
        segment_table = create_summary_table(segment_risk_df)
        
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H3("Risk Dashboard", className="mb-4"),
                    html.P("Identify entities and segments at risk of churning")
                ])
            ]),
            
            # Summary cards
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"{high_risk_count:,}", className="text-danger"),
                            html.P("High Risk Entities", className="mb-0")
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"{avg_risk_score:.1f}", className="text-warning"),
                            html.P("Average Risk Score", className="mb-0")
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"{high_risk_segments}", className="text-danger"),
                            html.P("High Risk Segments", className="mb-0")
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=avg_gauge, config={'displayModeBar': False},
                                    style={'height': '200px'})
                        ])
                    ])
                ], width=3)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Entity Risk Analysis")),
                        dbc.CardBody([
                            dcc.Graph(figure=scatter_chart, config={'displayModeBar': False})
                        ])
                    ])
                ], width=12)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Segment Risk Scores")),
                        dbc.CardBody([
                            dcc.Graph(figure=segment_bars, config={'displayModeBar': False})
                        ])
                    ])
                ], width=12)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Top 20 High-Risk Entities")),
                        dbc.CardBody([
                            top_risk_table
                        ], style={'overflowX': 'auto'})
                    ])
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Segment Risk Details")),
                        dbc.CardBody([
                            segment_table
                        ], style={'overflowX': 'auto'})
                    ])
                ], width=6)
            ])
        ], fluid=True)
    
    
    # Entity Search Tab
    @app.callback(
        Output('entity-content', 'children'),
        [Input('search-entity-button', 'n_clicks')],
        [State('entity-search-input', 'value'),
         State('snapshot-data', 'data')]
    )
    def search_entity(n_clicks, entity_id, snapshot_dict):
        """Search for entity and display details."""
        
        if n_clicks is None or entity_id is None or snapshot_dict is None:
            return dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.H3("Entity Search", className="mb-4"),
                        html.P("Enter an entity ID in the sidebar and click 'Search Entity' to view details")
                    ])
                ])
            ], fluid=True)
        
        snapshot = pd.DataFrame(snapshot_dict)
        
        # Calculate entity metrics
        entity_metrics = calculate_entity_metrics(snapshot, entity_id)
        
        if entity_metrics is None:
            return dbc.Container([
                dbc.Alert(f"Entity '{entity_id}' not found in the dataset", color="warning")
            ], fluid=True)
        
        # Create mock journey
        entity_history = [
            {'month': '202406', 'segment': entity_metrics['base_segment'], 
             'revenue': entity_metrics['base_total_revenue'], 'status': 'Base'},
            {'month': '202411', 'segment': entity_metrics['current_segment'], 
             'revenue': entity_metrics['current_total_revenue'], 'status': entity_metrics['status']}
        ]
        
        journey_chart = create_entity_journey_timeline(entity_history)
        
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H3(f"Entity Details: {entity_id}", className="mb-4")
                ])
            ]),
            
            # Summary cards
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Base Segment"),
                            html.H4(str(entity_metrics['base_segment']) if entity_metrics['base_segment'] else "N/A", 
                                   className="text-primary")
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Current Segment"),
                            html.H4(str(entity_metrics['current_segment']) if entity_metrics['current_segment'] else "N/A", 
                                   className="text-success")
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Status"),
                            html.H4(entity_metrics['status'], className="text-info")
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Revenue Change"),
                            html.H4(f"${entity_metrics['revenue_change']:,.0f}", 
                                   className="text-success" if entity_metrics['revenue_change'] >= 0 else "text-danger"),
                            html.P(f"{entity_metrics['revenue_change_pct']:.1f}%", className="mb-0")
                        ])
                    ])
                ], width=3)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Entity Journey Timeline")),
                        dbc.CardBody([
                            dcc.Graph(figure=journey_chart, config={'displayModeBar': False})
                        ])
                    ])
                ], width=12)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Detailed Metrics")),
                        dbc.CardBody([
                            html.Table([
                                html.Tr([html.Th("Metric"), html.Th("Value")]),
                                html.Tr([html.Td("Entity ID"), html.Td(entity_metrics['entity_id'])]),
                                html.Tr([html.Td("Base Total Revenue"), html.Td(f"${entity_metrics['base_total_revenue']:,.2f}")]),
                                html.Tr([html.Td("Current Total Revenue"), html.Td(f"${entity_metrics['current_total_revenue']:,.2f}")]),
                                html.Tr([html.Td("Revenue Change ($)"), html.Td(f"${entity_metrics['revenue_change']:,.2f}")]),
                                html.Tr([html.Td("Revenue Change (%)"), html.Td(f"{entity_metrics['revenue_change_pct']:.2f}%")]),
                            ], className="table table-striped")
                        ])
                    ])
                ], width=12)
            ])
        ], fluid=True)
    
    
    # Export to Excel
    @app.callback(
        Output('export-status', 'children'),
        [Input('export-excel-button', 'n_clicks')],
        [State('snapshot-data', 'data'),
         State('current-month-store', 'data'),
         State('metric-selector', 'value')]
    )
    def export_excel(n_clicks, snapshot_dict, current_month, selected_metric):
        """Export analysis to Excel."""
        
        if n_clicks is None or snapshot_dict is None:
            return html.Div()
        
        try:
            snapshot = pd.DataFrame(snapshot_dict)
            
            # Generate all views
            views = {}
            views['Summary'] = generate_summary_view(snapshot, selected_metric)
            views['Matrix'] = generate_movement_matrix(snapshot, selected_metric)
            views['Product Mix'] = calculate_product_mix(snapshot)
            views['Cohorts'] = identify_segment_cohorts(snapshot)
            views['Cohort Revenue'] = calculate_cohort_revenue_metrics(snapshot)
            
            # Export
            filepath = export_to_excel(views, base_month, current_month)
            
            return dbc.Alert([
                html.I(className="bi bi-check-circle-fill me-2"),
                f"Successfully exported to: {filepath}"
            ], color="success", dismissable=True)
            
        except Exception as e:
            return dbc.Alert([
                html.I(className="bi bi-exclamation-triangle-fill me-2"),
                f"Export failed: {str(e)}"
            ], color="danger", dismissable=True)
    
    
    # Export Risk Report
    @app.callback(
        Output('export-status', 'children', allow_duplicate=True),
        [Input('export-risk-button', 'n_clicks')],
        [State('snapshot-data', 'data'),
         State('current-month-store', 'data')],
        prevent_initial_call=True
    )
    def export_risk(n_clicks, snapshot_dict, current_month):
        """Export risk report to Excel."""
        
        if n_clicks is None or snapshot_dict is None:
            return html.Div()
        
        try:
            snapshot = pd.DataFrame(snapshot_dict)
            
            # Calculate risk metrics
            entity_risk_df = calculate_churn_risk_score(snapshot)
            segment_risk_df = identify_at_risk_segments(snapshot)
            
            # Export
            filepath = export_risk_report(entity_risk_df, segment_risk_df, base_month, current_month)
            
            return dbc.Alert([
                html.I(className="bi bi-check-circle-fill me-2"),
                f"Successfully exported risk report to: {filepath}"
            ], color="success", dismissable=True)
            
        except Exception as e:
            return dbc.Alert([
                html.I(className="bi bi-exclamation-triangle-fill me-2"),
                f"Export failed: {str(e)}"
            ], color="danger", dismissable=True)