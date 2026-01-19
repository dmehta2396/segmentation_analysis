"""
Sankey diagram data generation
"""

from src.utils.dates import timer
from .metrics import calculate_metric


@timer
def generate_sankey_data(snapshot, metric: str = 'count') -> dict:
    """Generate data for Sankey diagram showing segment flows."""
    
    print(f"Generating Sankey for metric: {metric}")
    
    # Get unique segments
    base_segments = sorted(snapshot['base_segment'].dropna().unique())
    curr_segments = sorted(snapshot['current_segment'].dropna().unique())
    
    # Create node labels
    base_labels = [f"{seg} (Base)" for seg in base_segments]
    curr_labels = [f"{seg} (Current)" for seg in curr_segments]
    all_labels = base_labels + curr_labels + ['New (System)', 'Lost (System)']
    
    # Create index mapping
    label_to_idx = {label: idx for idx, label in enumerate(all_labels)}
    
    # Prepare flow data
    sources = []
    targets = []
    values = []
    
    # Flow from base to current
    for base_seg in base_segments:
        base_idx = label_to_idx[f"{base_seg} (Base)"]
        
        for curr_seg in curr_segments:
            curr_idx = label_to_idx[f"{curr_seg} (Current)"]
            
            flow = snapshot[
                (snapshot['base_segment'] == base_seg) &
                (snapshot['current_segment'] == curr_seg)
            ]
            
            value = calculate_metric(flow, 'current', metric)
            
            if value > 0:
                sources.append(base_idx)
                targets.append(curr_idx)
                values.append(value)
        
        # Lost from system
        lost_idx = label_to_idx['Lost (System)']
        lost = snapshot[
            (snapshot['base_segment'] == base_seg) &
            (snapshot['current_segment'].isna())
        ]
        value = calculate_metric(lost, 'base', metric)
        
        if value > 0:
            sources.append(base_idx)
            targets.append(lost_idx)
            values.append(value)
    
    # New to system
    new_idx = label_to_idx['New (System)']
    for curr_seg in curr_segments:
        curr_idx = label_to_idx[f"{curr_seg} (Current)"]
        
        new = snapshot[
            (snapshot['current_segment'] == curr_seg) &
            (snapshot['base_segment'].isna())
        ]
        value = calculate_metric(new, 'current', metric)
        
        if value > 0:
            sources.append(new_idx)
            targets.append(curr_idx)
            values.append(value)
    
    sankey_data = {
        'labels': all_labels,
        'sources': sources,
        'targets': targets,
        'values': values
    }
    
    print(f"  Created {len(values)} flows between {len(all_labels)} nodes")
    
    return sankey_data