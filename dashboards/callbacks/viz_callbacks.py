"""
Visualization callbacks
"""

import pandas as pd
import time
from dash import Input, Output
from dash import html

from src.analysis.summary import generate_summary_view
from src.analysis.matrix import generate_movement_matrix
from src.analysis.sankey import generate_sankey_data
from src.visualization.charts import (
    create_comparison_chart,
    create_summary_bar_chart,
    create_movement_heatmap,
    create_sankey_diagram
)
from src.visualization.tables import create_summary_table
from dashboards.layouts.main_content import create_main_content_layout


def register_viz_callbacks(app, base_month):
    """Register callbacks for visualization updates."""
    
    @app.callback(
        Output('overview-content', 'children'),
        [Input('analysis-tabs', 'active_tab'),
         Input('snapshot-data', 'data'),
         Input('metric-selector', 'value'),
         Input('current-month-store', 'data')]
    )
    def update_overview_tab(active_tab, snapshot_dict, selected_metric, current_month):
        """Update overview tab with main visualizations."""
        
        if active_tab != 'tab-overview' or snapshot_dict is None:
            return html.Div()
        
        start_time = time.time()
        print(f"\n{'='*60}")
        print(f"UPDATING OVERVIEW TAB: Metric={selected_metric}")
        print(f"{'='*60}")
        
        # Convert back to DataFrame
        snapshot = pd.DataFrame(snapshot_dict)
        print(f"Snapshot shape: {snapshot.shape}")
        
        # Generate views
        summary_df = generate_summary_view(snapshot, selected_metric)
        matrix_df = generate_movement_matrix(snapshot, selected_metric)
        sankey_data = generate_sankey_data(snapshot, selected_metric)
        
        # Create visualizations
        metric_display = selected_metric.upper().replace('_', ' ') if selected_metric != 'count' else 'COUNT'
        
        comparison_chart = create_comparison_chart(summary_df, metric_display)
        summary_chart = create_summary_bar_chart(summary_df, metric_display)
        heatmap = create_movement_heatmap(matrix_df, metric_display)
        sankey = create_sankey_diagram(sankey_data, metric_display)
        
        summary_table = create_summary_table(summary_df)
        matrix_table = create_summary_table(matrix_df)
        
        # Create layout
        layout = create_main_content_layout(
            base_month, current_month, metric_display,
            comparison_chart, sankey, summary_chart,
            heatmap, summary_table, matrix_table
        )
        
        end_time = time.time()
        print(f"⏱️  Overview tab update: {end_time - start_time:.2f} seconds")
        print(f"{'='*60}\n")
        
        return layout