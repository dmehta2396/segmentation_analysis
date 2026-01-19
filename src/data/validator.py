"""
Data validation functions
"""

import pandas as pd
from src.config.settings import SEGMENT_COLS, METRICS_COLS


def validate_segmentation_data(df: pd.DataFrame, file_name: str) -> bool:
    """Validate segmentation data structure."""
    required_cols = [SEGMENT_COLS['entity'], SEGMENT_COLS['month'], SEGMENT_COLS['segment']]
    
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing columns in {file_name}: {missing_cols}")
    
    # Check for duplicates
    duplicates = df.duplicated(subset=[SEGMENT_COLS['entity']]).sum()
    if duplicates > 0:
        print(f"  ⚠️  Warning: {duplicates} duplicate entities in {file_name}")
    
    # Check for null segments
    null_segments = df[SEGMENT_COLS['segment']].isna().sum()
    if null_segments > 0:
        print(f"  ⚠️  Warning: {null_segments} entities with null segments in {file_name}")
    
    return True


def validate_metrics_data(df: pd.DataFrame) -> bool:
    """Validate metrics data structure."""
    required_cols = [METRICS_COLS['entity'], METRICS_COLS['month']]
    
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing columns in metrics: {missing_cols}")
    
    return True