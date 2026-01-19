"""
Snapshot generation callbacks
"""

import pandas as pd
import time
from dash import Input, Output, State
import dash_bootstrap_components as dbc
from dash import html

from src.data.loader import load_curr_seg
from src.data.processor import create_snapshot
from src.analysis.metrics import get_available_metrics


def register_snapshot_callbacks(app, base_seg, metrics_glbl, base_month):
    """Register callbacks for snapshot generation."""
    
    @app.callback(
        [Output('snapshot-data', 'data'),
         Output('current-month-store', 'data'),
         Output('status-message', 'children'),
         Output('metric-selector', 'options'),
         Output('metric-selector', 'value')],
        [Input('submit-button', 'n_clicks')],
        [State('month-selector', 'value')]
    )
    def generate_snapshot_data(n_clicks, current_month):
        """Generate snapshot when button is clicked."""
        
        if n_clicks is None:
            return None, None, dbc.Alert(
                "Select a comparison month and click 'Generate Analysis' to begin.", 
                color="info"
            ), [{'label': 'Count', 'value': 'count'}], 'count'
        
        try:
            start_time = time.time()
            print(f"\n{'='*60}")
            print(f"GENERATING ANALYSIS: {base_month} vs {current_month}")
            print(f"{'='*60}")
            
            # Load current month segmentation
            curr_seg = load_curr_seg(current_month)
            
            # Create snapshot
            snapshot = create_snapshot(base_seg, curr_seg, metrics_glbl)
            
            # Get available metrics
            metrics = get_available_metrics(snapshot)
            metric_options = [{'label': 'Count', 'value': 'count'}] + \
                            [{'label': m.upper().replace('_', ' '), 'value': m} for m in metrics]
            
            # Convert to dict for JSON serialization
            snapshot_dict = snapshot.to_dict('records')
            
            end_time = time.time()
            duration = end_time - start_time
            
            status_msg = dbc.Alert([
                html.I(className="bi bi-check-circle-fill me-2"),
                f"✓ Analysis complete in {duration:.1f}s! "
                f"Comparing {base_month} vs {current_month}. "
                f"Found {len(snapshot):,} entities and {len(metrics)} metrics."
            ], color="success")
            
            print(f"⏱️  Total callback time: {duration:.2f} seconds")
            print(f"{'='*60}\n")
            
            return snapshot_dict, current_month, status_msg, metric_options, 'count'
            
        except Exception as e:
            print(f"\nERROR: {str(e)}\n")
            import traceback
            traceback.print_exc()
            
            error_msg = dbc.Alert([
                html.I(className="bi bi-exclamation-triangle-fill me-2"),
                f"Error: {str(e)}"
            ], color="danger")
            return None, None, error_msg, [{'label': 'Count', 'value': 'count'}], 'count'