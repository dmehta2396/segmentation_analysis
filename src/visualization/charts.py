"""
Chart creation functions
"""

import plotly.graph_objects as go
from .colors import MOVEMENT_COLORS, SANKEY_NODE_COLORS, CHART_COLORS


def create_comparison_chart(df, metric_name: str):
    """Create grouped bar chart comparing base vs current."""
    df_plot = df[df['Segment'] != 'TOTAL'].copy()
    
    if len(df_plot) == 0:
        return go.Figure().add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Base',
        x=df_plot['Segment'],
        y=df_plot['Base'],
        marker_color=CHART_COLORS['secondary'],
        text=df_plot['Base'].apply(lambda x: f'{x:,.0f}'),
        textposition='auto',
    ))
    
    fig.add_trace(go.Bar(
        name='Current',
        x=df_plot['Segment'],
        y=df_plot['Current'],
        marker_color=CHART_COLORS['primary'],
        text=df_plot['Current'].apply(lambda x: f'{x:,.0f}'),
        textposition='auto',
    ))
    
    fig.update_layout(
        xaxis_title='Segment',
        yaxis_title=metric_name,
        barmode='group',
        template='plotly_white',
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    return fig


def create_summary_bar_chart(df, metric_name: str):
    """Create waterfall-style bar chart for movement breakdown."""
    df_plot = df[df['Segment'] != 'TOTAL'].copy()
    
    if len(df_plot) == 0:
        return go.Figure().add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    fig = go.Figure()
    
    categories = ['Retained', 'New (System)', 'Added (Other Seg)', 
                 'Lost (Other Seg)', 'Lost (System)']
    
    for category in categories:
        if category in df_plot.columns:
            values = df_plot[category].values
            if 'Lost' in category:
                values = -values
            
            fig.add_trace(go.Bar(
                name=category,
                x=df_plot['Segment'],
                y=values,
                marker_color=MOVEMENT_COLORS.get(category, '#808080'),
                text=[f'{abs(v):,.0f}' for v in values],
                textposition='auto',
            ))
    
    fig.update_layout(
        xaxis_title='Segment',
        yaxis_title=metric_name,
        barmode='relative',
        template='plotly_white',
        height=500,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        margin=dict(l=50, r=50, t=50, b=100)
    )
    
    return fig


def create_movement_heatmap(df, metric_name: str):
    """Create heatmap for movement matrix."""
    df_plot = df[df[df.columns[0]] != 'Total In'].copy()
    if 'Total Out' in df_plot.columns:
        df_plot = df_plot.drop(columns=['Total Out'])
    
    if len(df_plot) == 0:
        return go.Figure().add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    df_plot = df_plot.set_index(df_plot.columns[0])
    
    fig = go.Figure(data=go.Heatmap(
        z=df_plot.values,
        x=df_plot.columns,
        y=df_plot.index,
        colorscale='Blues',
        text=df_plot.values,
        texttemplate='%{text:,.0f}',
        textfont={"size": 10},
        hoverongaps=False,
        hovertemplate='From: %{y}<br>To: %{x}<br>' + metric_name + ': %{z:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        xaxis_title='Current Segment',
        yaxis_title='Base Segment',
        template='plotly_white',
        height=500,
        margin=dict(l=100, r=50, t=50, b=50)
    )
    
    return fig


def create_sankey_diagram(sankey_data, metric_name: str):
    """Create Sankey diagram for segment flows."""
    
    if len(sankey_data['values']) == 0:
        return go.Figure().add_annotation(
            text="No flow data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    # Assign colors to nodes
    node_colors = []
    for label in sankey_data['labels']:
        if '(Base)' in label:
            node_colors.append(SANKEY_NODE_COLORS['base'])
        elif '(Current)' in label:
            node_colors.append(SANKEY_NODE_COLORS['current'])
        elif 'New' in label:
            node_colors.append(SANKEY_NODE_COLORS['new'])
        elif 'Lost' in label:
            node_colors.append(SANKEY_NODE_COLORS['lost'])
        else:
            node_colors.append('rgba(128, 128, 128, 0.8)')
    
    # Assign colors to links
    link_colors = []
    for src, tgt in zip(sankey_data['sources'], sankey_data['targets']):
        target_label = sankey_data['labels'][tgt]
        if 'Lost' in target_label:
            link_colors.append('rgba(199, 62, 29, 0.3)')
        elif 'New' in sankey_data['labels'][src]:
            link_colors.append('rgba(6, 167, 125, 0.3)')
        else:
            link_colors.append('rgba(46, 134, 171, 0.3)')
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='white', width=0.5),
            label=sankey_data['labels'],
            color=node_colors,
            customdata=[label.split(' (')[0] for label in sankey_data['labels']],
            hovertemplate='%{customdata}<br>Total: %{value:,.0f}<extra></extra>'
        ),
        link=dict(
            source=sankey_data['sources'],
            target=sankey_data['targets'],
            value=sankey_data['values'],
            color=link_colors,
            hovertemplate='%{source.customdata} → %{target.customdata}<br>' + 
                         metric_name + ': %{value:,.0f}<extra></extra>'
        )
    )])
    
    fig.update_layout(
        title=dict(
            text=f"Segment Flow: Base → Current",
            x=0.5,
            xanchor='center'
        ),
        font=dict(size=11),
        height=600,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig