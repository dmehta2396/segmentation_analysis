"""
Metric calculation functions
"""

import pandas as pd
from src.utils.dates import timer


def get_available_metrics(snapshot) -> list:
    """Get list of available metrics from snapshot."""
    metrics = []
    for col in snapshot.columns:
        if col.startswith('base_'):
            metric = col.replace('base_', '')
            metrics.append(metric)
    return sorted(metrics)


def calculate_metric(df, period: str, metric: str) -> float:
    """Calculate metric value for a dataframe."""
    if len(df) == 0:
        return 0.0
    
    if metric == 'count':
        return len(df)
    else:
        col_name = f'{period}_{metric}'
        if col_name in df.columns:
            return df[col_name].sum()
        else:
            return 0.0


@timer
def calculate_product_mix(snapshot: pd.DataFrame, segment: str = None) -> pd.DataFrame:
    """
    Calculate product revenue mix by segment.
    
    Args:
        snapshot: Snapshot dataframe
        segment: Specific segment to analyze (None for all)
        
    Returns:
        DataFrame with product mix percentages
    """
    print(f"Calculating product mix{f' for {segment}' if segment else ' for all segments'}")
    
    # Filter by segment if specified
    if segment:
        df = snapshot[snapshot['current_segment'] == segment].copy()
    else:
        df = snapshot[snapshot['current_segment'].notna()].copy()
    
    # Get all product columns
    product_cols = [col for col in df.columns if col.startswith('current_') and '_rev_wf' in col]
    
    if len(product_cols) == 0:
        print("  No product revenue columns found")
        return pd.DataFrame()
    
    # Calculate total revenue per product
    product_revenues = {}
    for col in product_cols:
        product = col.replace('current_', '').replace('_rev_wf', '')
        product_revenues[product] = df[col].sum()
    
    # Create DataFrame
    mix_df = pd.DataFrame({
        'Product': list(product_revenues.keys()),
        'Revenue': list(product_revenues.values())
    })
    
    # Calculate percentages
    total_revenue = mix_df['Revenue'].sum()
    mix_df['Percentage'] = (mix_df['Revenue'] / total_revenue * 100).round(2)
    
    # Sort by revenue descending
    mix_df = mix_df.sort_values('Revenue', ascending=False).reset_index(drop=True)
    
    print(f"  Total revenue: ${total_revenue:,.2f}")
    print(f"  Top product: {mix_df.iloc[0]['Product']} ({mix_df.iloc[0]['Percentage']}%)")
    
    return mix_df


@timer
def calculate_segment_product_matrix(snapshot: pd.DataFrame) -> pd.DataFrame:
    """
    Create matrix of segments vs products showing revenue contribution.
    
    Args:
        snapshot: Snapshot dataframe
        
    Returns:
        DataFrame with segments as rows, products as columns
    """
    print("Calculating segment-product matrix")
    
    segments = sorted(snapshot['current_segment'].dropna().unique())
    
    # Get product columns
    product_cols = [col for col in snapshot.columns if col.startswith('current_') and '_rev_wf' in col]
    products = [col.replace('current_', '').replace('_rev_wf', '') for col in product_cols]
    
    # Build matrix
    matrix_data = []
    
    for segment in segments:
        seg_data = {'Segment': segment}
        seg_df = snapshot[snapshot['current_segment'] == segment]
        
        for product, col in zip(products, product_cols):
            seg_data[product] = seg_df[col].sum()
        
        matrix_data.append(seg_data)
    
    matrix = pd.DataFrame(matrix_data)
    
    print(f"  Matrix shape: {len(segments)} segments × {len(products)} products")
    
    return matrix


@timer
def calculate_entity_metrics(snapshot: pd.DataFrame, entity_id: str) -> dict:
    """
    Calculate detailed metrics for a specific entity.
    
    Args:
        snapshot: Snapshot dataframe
        entity_id: Entity identifier
        
    Returns:
        Dictionary with entity metrics
    """
    print(f"Calculating metrics for entity: {entity_id}")
    
    entity_data = snapshot[snapshot['entity'] == entity_id]
    
    if len(entity_data) == 0:
        print(f"  Entity {entity_id} not found")
        return None
    
    entity = entity_data.iloc[0]
    
    metrics = {
        'entity_id': entity_id,
        'base_segment': entity.get('base_segment', None),
        'current_segment': entity.get('current_segment', None),
        'status': entity.get('status', None),
    }
    
    # Calculate total revenues
    base_rev_cols = [col for col in snapshot.columns if col.startswith('base_') and '_rev_wf' in col]
    curr_rev_cols = [col for col in snapshot.columns if col.startswith('current_') and '_rev_wf' in col]
    
    metrics['base_total_revenue'] = sum(entity[col] for col in base_rev_cols if col in entity.index)
    metrics['current_total_revenue'] = sum(entity[col] for col in curr_rev_cols if col in entity.index)
    metrics['revenue_change'] = metrics['current_total_revenue'] - metrics['base_total_revenue']
    metrics['revenue_change_pct'] = (metrics['revenue_change'] / metrics['base_total_revenue'] * 100) if metrics['base_total_revenue'] > 0 else 0
    
    print(f"  Base: {metrics['base_segment']}, Current: {metrics['current_segment']}")
    print(f"  Revenue change: ${metrics['revenue_change']:,.2f} ({metrics['revenue_change_pct']:.1f}%)")
    
    return metrics