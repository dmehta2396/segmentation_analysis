"""
Summary view generation
"""

import pandas as pd
from src.utils.dates import timer
from .metrics import calculate_metric


@timer
def generate_summary_view(snapshot: pd.DataFrame, metric: str = 'count') -> pd.DataFrame:
    """Generate summary view showing segment statistics."""
    
    print(f"Generating summary for metric: {metric}")
    
    # Get all unique segments
    base_segments = set(snapshot['base_segment'].dropna().unique())
    curr_segments = set(snapshot['current_segment'].dropna().unique())
    all_segments = sorted(base_segments | curr_segments)
    
    print(f"  Segments: {all_segments}")
    
    summary_data = []
    
    for segment in all_segments:
        row = {'Segment': segment}
        
        # Base
        base_entities = snapshot[snapshot['base_segment'] == segment]
        row['Base'] = calculate_metric(base_entities, 'base', metric)
        
        # Current
        curr_entities = snapshot[snapshot['current_segment'] == segment]
        row['Current'] = calculate_metric(curr_entities, 'current', metric)
        
        # Retained
        retained = snapshot[
            (snapshot['base_segment'] == segment) &
            (snapshot['current_segment'] == segment)
        ]
        row['Retained'] = calculate_metric(retained, 'current', metric)
        
        # New (System)
        new_system = snapshot[
            (snapshot['current_segment'] == segment) &
            (snapshot['base_segment'].isna())
        ]
        row['New (System)'] = calculate_metric(new_system, 'current', metric)
        
        # Added (Other Seg)
        added = snapshot[
            (snapshot['current_segment'] == segment) &
            (snapshot['base_segment'].notna()) &
            (snapshot['base_segment'] != segment)
        ]
        row['Added (Other Seg)'] = calculate_metric(added, 'current', metric)
        
        # Lost (Other Seg)
        lost_other = snapshot[
            (snapshot['base_segment'] == segment) &
            (snapshot['current_segment'].notna()) &
            (snapshot['current_segment'] != segment)
        ]
        row['Lost (Other Seg)'] = calculate_metric(lost_other, 'base', metric)
        
        # Lost (System)
        lost_system = snapshot[
            (snapshot['base_segment'] == segment) &
            (snapshot['current_segment'].isna())
        ]
        row['Lost (System)'] = calculate_metric(lost_system, 'base', metric)
        
        # Net Change
        row['Net Change'] = row['Current'] - row['Base']
        
        summary_data.append(row)
    
    df = pd.DataFrame(summary_data)
    
    # Add totals row
    totals = {'Segment': 'TOTAL'}
    for col in df.columns:
        if col != 'Segment':
            totals[col] = df[col].sum()
    
    totals_df = pd.DataFrame([totals], index=[0])
    df = pd.concat([df, totals_df], ignore_index=True)
    
    print(f"  Total Base: {df[df['Segment']=='TOTAL']['Base'].values[0]:,.0f}")
    print(f"  Total Current: {df[df['Segment']=='TOTAL']['Current'].values[0]:,.0f}")
    
    return df