"""
Data loading functions
"""

import pandas as pd
import glob
import os
from pathlib import Path
from src.config.settings import DATA_DIR, SEGMENT_COLS, METRICS_COLS
from src.utils.dates import timer


@timer
def get_available_current_months(data_dir: str = None) -> list:
    """
    Scan data directory for available curr_seg_YYYYMM.csv files.
    
    Returns:
        List of available months in YYYYMM format
    """
    if data_dir is None:
        data_dir = DATA_DIR
    
    pattern = os.path.join(data_dir, 'curr_seg_*.csv')
    files = glob.glob(pattern)
    
    months = []
    for file in files:
        filename = Path(file).stem
        if filename.startswith('curr_seg_'):
            month_str = filename.replace('curr_seg_', '')
            try:
                month = int(month_str)
                months.append(month)
                print(f"  Found: {file} -> Month {month}")
            except ValueError:
                print(f"  Skipped: {file} (invalid format)")
    
    months = sorted(months)
    print(f"\nTotal available months: {len(months)}")
    return months


@timer
def load_base_seg(file_path: str = None) -> pd.DataFrame:
    """Load base segmentation file."""
    if file_path is None:
        file_path = os.path.join(DATA_DIR, 'base_seg.csv')
    
    print(f"Loading from: {file_path}")
    base_seg = pd.read_csv(file_path)
    
    print(f"  Rows: {len(base_seg):,}")
    print(f"  Unique entities: {base_seg[SEGMENT_COLS['entity']].nunique():,}")
    print(f"  Segments: {sorted(base_seg[SEGMENT_COLS['segment']].unique())}")
    
    return base_seg


@timer
def load_curr_seg(month: int, data_dir: str = None) -> pd.DataFrame:
    """Load current segmentation file for specific month."""
    if data_dir is None:
        data_dir = DATA_DIR
    
    file_path = os.path.join(data_dir, f'curr_seg_{month}.csv')
    print(f"Loading from: {file_path}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    curr_seg = pd.read_csv(file_path)
    
    print(f"  Rows: {len(curr_seg):,}")
    print(f"  Unique entities: {curr_seg[SEGMENT_COLS['entity']].nunique():,}")
    print(f"  Segments: {sorted(curr_seg[SEGMENT_COLS['segment']].unique())}")
    
    return curr_seg


@timer
def load_metrics_glbl(file_path: str = None) -> pd.DataFrame:
    """Load metrics global file."""
    if file_path is None:
        file_path = os.path.join(DATA_DIR, 'rev_glbl.csv')
    
    print(f"Loading from: {file_path}")
    metrics_glbl = pd.read_csv(file_path)
    
    print(f"  Rows: {len(metrics_glbl):,}")
    print(f"  Unique entities: {metrics_glbl[METRICS_COLS['entity']].nunique():,}")
    print(f"  Month range: {metrics_glbl[METRICS_COLS['month']].min()} to {metrics_glbl[METRICS_COLS['month']].max()}")
    
    return metrics_glbl