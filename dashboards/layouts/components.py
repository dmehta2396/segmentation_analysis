"""
Reusable dashboard components
"""

import dash_bootstrap_components as dbc
from dash import html


def create_status_alert(message: str, alert_type: str = "info"):
    """Create status alert message."""
    
    icons = {
        'info': 'bi-info-circle-fill',
        'success': 'bi-check-circle-fill',
        'warning': 'bi-exclamation-triangle-fill',
        'danger': 'bi-exclamation-triangle-fill'
    }
    
    return dbc.Alert([
        html.I(className=f"{icons.get(alert_type, 'bi-info-circle-fill')} me-2"),
        message
    ], color=alert_type)