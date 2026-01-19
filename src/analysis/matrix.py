"""
Movement matrix generation
"""

import pandas as pd
from src.utils.dates import timer
from .metrics import calculate_metric


@timer
def generate_movement_matrix(snapshot: pd.DataFrame, metric: str = 'count') -> pd.DataFrame:
    """Generate movement matrix showing flows between segments."""
    
    print(f"Generating matrix for metric: {metric}")
    
    base_segments = sorted(snapshot['base_segment'].dropna().unique())
    curr_segments = sorted(snapshot['current_segment'].dropna().unique())
    
    # Add special categories
    all_base = base_segments + ['New']
    all_curr = curr_segments + ['Lost']
    
    # Initialize matrix
    matrix = pd.DataFrame(
        index=all_base,
        columns=all_curr,
        data=0.0
    )
    
    # Fill movements
    for base_seg in base_segments:
        for curr_seg in curr_segments:
            movement = snapshot[
                (snapshot['base_segment'] == base_seg) &
                (snapshot['current_segment'] == curr_seg)
            ]
            matrix.loc[base_seg, curr_seg] = calculate_metric(movement, 'current', metric)
        
        # Lost
        lost = snapshot[
            (snapshot['base_segment'] == base_seg) &
            (snapshot['current_segment'].isna())
        ]
        matrix.loc[base_seg, 'Lost'] = calculate_metric(lost, 'base', metric)
    
    # New row
    for curr_seg in curr_segments:
        new = snapshot[
            (snapshot['current_segment'] == curr_seg) &
            (snapshot['base_segment'].isna())
        ]
        matrix.loc['New', curr_seg] = calculate_metric(new, 'current', metric)
    
    # Totals
    matrix['Total Out'] = matrix.sum(axis=1)
    matrix.loc['Total In'] = matrix.sum(axis=0)
    
    matrix = matrix.reset_index()
    matrix = matrix.rename(columns={'index': 'Base → Current'})
    
    return matrix