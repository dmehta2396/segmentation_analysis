"""
Advanced chart creation functions
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from .colors import CHART_COLORS


def create_product_mix_pie(product_mix_df, metric_name: str):
    """Create pie chart for product mix."""
    
    if len(product_mix_df) == 0:
        return go.Figure().add_annotation(
            text="No product data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    fig = go.Figure(data=[go.Pie(
        labels=product_mix_df['Product'],
        values=product_mix_df['Revenue'],
        hole=0.4,
        textposition='auto',
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>' +
                     'Revenue: $%{value:,.0f}<br>' +
                     'Percentage: %{percent}<br>' +
                     '<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(
            text=f"Product Mix - {metric_name}",
            x=0.5,
            xanchor='center'
        ),
        height=400,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05)
    )
    
    return fig


def create_segment_product_heatmap(matrix_df):
    """Create heatmap showing revenue by segment and product."""
    
    if len(matrix_df) == 0:
        return go.Figure().add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    segments = matrix_df['Segment'].values
    products = [col for col in matrix_df.columns if col != 'Segment']
    
    z_data = matrix_df[products].values
    
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=products,
        y=segments,
        colorscale='Viridis',
        text=z_data,
        texttemplate='$%{text:,.0f}',
        textfont={"size": 9},
        hoverongaps=False,
        hovertemplate='Segment: %{y}<br>Product: %{x}<br>Revenue: $%{z:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Product Revenue by Segment',
        xaxis_title='Product',
        yaxis_title='Segment',
        height=600,
        template='plotly_white'
    )
    
    return fig


def create_risk_gauge(risk_score: float, title: str = "Risk Score"):
    """Create gauge chart for risk score."""
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 24}},
        delta={'reference': 50, 'increasing': {'color': "red"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': '#06A77D'},
                {'range': [30, 60], 'color': '#F18F01'},
                {'range': [60, 100], 'color': '#C73E1D'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 60
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def create_cohort_retention_chart(cohort_df):
    """Create bar chart showing cohort retention rates."""
    
    if len(cohort_df) == 0:
        return go.Figure().add_annotation(
            text="No cohort data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Retention Rate',
        x=cohort_df['Base Segment'],
        y=cohort_df['Retention Rate'],
        marker_color=CHART_COLORS['success'],
        text=cohort_df['Retention Rate'].apply(lambda x: f'{x:.1f}%'),
        textposition='auto',
    ))
    
    fig.add_trace(go.Bar(
        name='Churn Rate',
        x=cohort_df['Base Segment'],
        y=cohort_df['Churn Rate'],
        marker_color=CHART_COLORS['danger'],
        text=cohort_df['Churn Rate'].apply(lambda x: f'{x:.1f}%'),
        textposition='auto',
    ))
    
    fig.update_layout(
        title='Cohort Retention and Churn Rates',
        xaxis_title='Base Segment (Cohort)',
        yaxis_title='Percentage (%)',
        barmode='group',
        template='plotly_white',
        height=500,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def create_cohort_revenue_waterfall(cohort_rev_df):
    """Create waterfall chart for cohort revenue changes."""
    
    if len(cohort_rev_df) == 0:
        return go.Figure().add_annotation(
            text="No cohort revenue data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    df = cohort_rev_df.sort_values('Revenue Change', ascending=False).head(10)
    
    fig = go.Figure(go.Waterfall(
        name="Revenue Change",
        orientation="v",
        measure=["relative"] * len(df),
        x=df['Cohort'],
        textposition="outside",
        text=df['Revenue Change'].apply(lambda x: f'${x:,.0f}'),
        y=df['Revenue Change'],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": CHART_COLORS['danger']}},
        increasing={"marker": {"color": CHART_COLORS['success']}},
    ))
    
    fig.update_layout(
        title="Top 10 Cohorts by Revenue Change",
        xaxis_title="Cohort",
        yaxis_title="Revenue Change ($)",
        template='plotly_white',
        height=500,
        showlegend=False
    )
    
    return fig


def create_risk_scatter(risk_df):
    """Create scatter plot of revenue vs risk score."""
    
    if len(risk_df) == 0:
        return go.Figure().add_annotation(
            text="No risk data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    df = risk_df.head(1000) if len(risk_df) > 1000 else risk_df
    
    color_map = {'High': '#C73E1D', 'Medium': '#F18F01', 'Low': '#06A77D'}
    
    fig = go.Figure()
    
    for risk_level in ['Low', 'Medium', 'High']:
        df_level = df[df['risk_level'] == risk_level]
        
        fig.add_trace(go.Scatter(
            x=df_level['current_revenue'],
            y=df_level['risk_score'],
            mode='markers',
            name=risk_level,
            marker=dict(
                color=color_map[risk_level],
                size=8,
                line=dict(width=0.5, color='white')
            ),
            text=df_level['entity'],
            hovertemplate='<b>%{text}</b><br>' +
                         'Revenue: $%{x:,.0f}<br>' +
                         'Risk Score: %{y}<br>' +
                         '<extra></extra>'
        ))
    
    fig.update_layout(
        title='Entity Risk Analysis: Revenue vs Risk Score',
        xaxis_title='Current Revenue ($)',
        yaxis_title='Risk Score',
        template='plotly_white',
        height=500,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_type="log"
    )
    
    return fig


def create_segment_risk_bars(segment_risk_df):
    """Create horizontal bar chart for segment risk scores."""
    
    if len(segment_risk_df) == 0:
        return go.Figure().add_annotation(
            text="No segment risk data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    df = segment_risk_df.sort_values('Risk Score', ascending=True)
    
    color_map = {'High': '#C73E1D', 'Medium': '#F18F01', 'Low': '#06A77D'}
    colors = [color_map[level] for level in df['Risk Level']]
    
    fig = go.Figure(go.Bar(
        x=df['Risk Score'],
        y=df['Segment'],
        orientation='h',
        marker_color=colors,
        text=df['Risk Score'],
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>' +
                     'Risk Score: %{x}<br>' +
                     'Churn Rate: %{customdata[0]:.1f}%<br>' +
                     'Revenue Change: %{customdata[1]:.1f}%<br>' +
                     '<extra></extra>',
        customdata=df[['Churn Rate %', 'Revenue Change %']].values
    ))
    
    fig.update_layout(
        title='Segment Risk Scores',
        xaxis_title='Risk Score',
        yaxis_title='Segment',
        template='plotly_white',
        height=600,
        showlegend=False
    )
    
    return fig


def create_entity_journey_timeline(entity_history: list):
    """Create timeline visualization for entity journey."""
    
    if len(entity_history) == 0:
        return go.Figure().add_annotation(
            text="No entity history available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    months = [h['month'] for h in entity_history]
    segments = [h['segment'] for h in entity_history]
    revenues = [h['revenue'] for h in entity_history]
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(
            x=months,
            y=segments,
            mode='lines+markers',
            name='Segment',
            line=dict(color=CHART_COLORS['primary'], width=3),
            marker=dict(size=10)
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Bar(
            x=months,
            y=revenues,
            name='Revenue',
            marker_color=CHART_COLORS['success'],
            opacity=0.6
        ),
        secondary_y=True
    )
    
    fig.update_xaxes(title_text="Month")
    fig.update_yaxes(title_text="Segment", secondary_y=False)
    fig.update_yaxes(title_text="Revenue ($)", secondary_y=True)
    
    fig.update_layout(
        title='Entity Journey Over Time',
        template='plotly_white',
        height=400,
        hovermode='x unified'
    )
    
    return fig