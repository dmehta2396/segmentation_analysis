"""
Data processing and transformation functions
"""

import pandas as pd
import numpy as np
import time
from src.config.settings import SEGMENT_COLS, METRICS_COLS, TTM_MONTHS
from src.utils.dates import get_ttm_months, timer
from src.utils.caching import save_to_cache, load_from_cache


def detect_metric_columns(metrics_glbl: pd.DataFrame) -> list:
    """Detect all metric columns."""
    all_cols = metrics_glbl.columns.tolist()
    metric_cols = [col for col in all_cols 
                   if col not in [METRICS_COLS['entity'], METRICS_COLS['month']]]
    print(f"  Detected {len(metric_cols)} metric columns")
    return metric_cols


@timer
def calculate_ttm_metrics(metrics_glbl: pd.DataFrame, month: int) -> pd.DataFrame:
    """Calculate TTM sum for each metric column by entity."""
    
    # Try to load from cache
    cache_id = f"ttm_{month}"
    cached_data = load_from_cache('metrics', cache_id)
    if cached_data is not None:
        return cached_data
    
    # Calculate TTM period
    ttm_months = get_ttm_months(month, TTM_MONTHS)
    print(f"  TTM Period: {min(ttm_months)} to {max(ttm_months)}")
    
    # Filter for TTM period
    metrics_ttm = metrics_glbl[metrics_glbl[METRICS_COLS['month']].isin(ttm_months)].copy()
    print(f"  Filtered rows: {len(metrics_ttm):,}")
    
    # Get metric columns
    metric_cols = detect_metric_columns(metrics_glbl)
    
    # Aggregate by entity
    agg_dict = {col: 'sum' for col in metric_cols}
    ttm_metrics = metrics_ttm.groupby(METRICS_COLS['entity'], as_index=False).agg(agg_dict)
    
    print(f"  Entities with metrics: {len(ttm_metrics):,}")
    
    # Save to cache
    save_to_cache(ttm_metrics, 'metrics', cache_id)
    
    return ttm_metrics


def classify_status_vectorized(snapshot: pd.DataFrame) -> pd.Series:
    """Classify entity movement status using vectorized operations."""
    base_na = snapshot['base_segment'].isna()
    curr_na = snapshot['current_segment'].isna()
    same_seg = snapshot['base_segment'] == snapshot['current_segment']
    
    status = pd.Series('', index=snapshot.index)
    status[base_na & ~curr_na] = 'New (System)'
    status[~base_na & curr_na] = 'Lost (System)'
    status[same_seg & ~base_na & ~curr_na] = 'Retained'
    status[~same_seg & ~base_na & ~curr_na] = 'Moved Internal'
    
    return status


@timer
def create_snapshot(base_seg: pd.DataFrame, 
                   curr_seg: pd.DataFrame, 
                   metrics_glbl: pd.DataFrame) -> pd.DataFrame:
    """Create snapshot comparing base vs current month with all metrics."""
    
    # Get months
    base_month = base_seg[SEGMENT_COLS['month']].iloc[0]
    current_month = curr_seg[SEGMENT_COLS['month']].iloc[0]
    
    # Try to load from cache
    cache_id = f"snapshot_{base_month}_{current_month}"
    cached_data = load_from_cache('snapshots', cache_id)
    if cached_data is not None:
        return cached_data
    
    print(f"Base Month: {base_month}")
    print(f"Current Month: {current_month}")
    
    # Prepare base data
    base = base_seg[[SEGMENT_COLS['entity'], SEGMENT_COLS['segment']]].copy()
    base.columns = ['entity', 'base_segment']
    print(f"Base entities: {len(base):,}")
    
    # Prepare current data
    curr = curr_seg[[SEGMENT_COLS['entity'], SEGMENT_COLS['segment']]].copy()
    curr.columns = ['entity', 'current_segment']
    print(f"Current entities: {len(curr):,}")
    
    # Merge segmentation
    print("\nMerging base and current...")
    snapshot = base.merge(curr, on='entity', how='outer')
    print(f"Snapshot entities: {len(snapshot):,}")
    
    # Classify status
    print("Classifying status...")
    snapshot['status'] = classify_status_vectorized(snapshot)
    print(snapshot['status'].value_counts())
    
    # Calculate TTM metrics
    base_metrics = calculate_ttm_metrics(metrics_glbl, base_month)
    curr_metrics = calculate_ttm_metrics(metrics_glbl, current_month)
    
    # Rename for merging
    base_metrics = base_metrics.rename(columns={METRICS_COLS['entity']: 'entity'})
    curr_metrics = curr_metrics.rename(columns={METRICS_COLS['entity']: 'entity'})
    
    # Get metric columns
    metric_cols = [col for col in base_metrics.columns if col != 'entity']
    
    # Add prefixes
    print("\nAdding metric prefixes...")
    base_rename = {col: f'base_{col}' for col in metric_cols}
    curr_rename = {col: f'current_{col}' for col in metric_cols}
    
    base_metrics.rename(columns=base_rename, inplace=True)
    curr_metrics.rename(columns=curr_rename, inplace=True)
    
    # Merge metrics
    print("Merging metrics...")
    snapshot = snapshot.merge(base_metrics, on='entity', how='left')
    del base_metrics
    
    snapshot = snapshot.merge(curr_metrics, on='entity', how='left')
    del curr_metrics
    
    # Fill NaN
    print("Filling missing values...")
    metric_cols_in_snapshot = [col for col in snapshot.columns 
                                if col not in ['entity', 'base_segment', 'current_segment', 'status']]
    snapshot[metric_cols_in_snapshot] = snapshot[metric_cols_in_snapshot].fillna(0)
    
    print(f"\nFinal snapshot: {len(snapshot):,} entities, {len(snapshot.columns)} columns")
    
    # Save to cache
    save_to_cache(snapshot, 'snapshots', cache_id)
    
    return snapshot