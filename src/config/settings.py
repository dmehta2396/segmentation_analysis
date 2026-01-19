"""
Configuration settings for the segmentation analysis system
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Directory paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = os.getenv('DATA_DIR', 'data/raw')
PROCESSED_DIR = os.getenv('PROCESSED_DIR', 'data/processed')
EXPORT_DIR = os.getenv('EXPORT_DIR', 'data/exports')

# Create directories if they don't exist
for directory in [DATA_DIR, PROCESSED_DIR, EXPORT_DIR]:
    os.makedirs(directory, exist_ok=True)
    os.makedirs(os.path.join(PROCESSED_DIR, 'snapshots'), exist_ok=True)
    os.makedirs(os.path.join(PROCESSED_DIR, 'metrics'), exist_ok=True)
    os.makedirs(os.path.join(EXPORT_DIR, 'excel'), exist_ok=True)
    os.makedirs(os.path.join(EXPORT_DIR, 'pdf'), exist_ok=True)

# Dashboard settings
DASHBOARD_HOST = os.getenv('DASHBOARD_HOST', '0.0.0.0')
DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', 8050))
DEBUG_MODE = os.getenv('DEBUG_MODE', 'True').lower() == 'true'

# Analysis settings
TTM_MONTHS = int(os.getenv('TTM_MONTHS', 12))
ENABLE_CACHING = os.getenv('ENABLE_CACHING', 'True').lower() == 'true'

# Column names configuration
# EDIT THESE IF YOUR COLUMN NAMES ARE DIFFERENT
SEGMENT_COLS = {
    'entity': 'glbl_enti_nbr',
    'month': 'segmentation_mnth',
    'segment': 'dmnt_seg_cd'
}

METRICS_COLS = {
    'entity': 'glbl_enti_nbr',
    'month': 'shp_dt_yyyymm'
}

# Visualization settings
SEGMENT_COLORS = {
    'Retained': '#2E86AB',
    'New (System)': '#06A77D',
    'Added (Other Seg)': '#A23B72',
    'Lost (Other Seg)': '#F18F01',
    'Lost (System)': '#C73E1D'
}

NODE_COLORS = {
    'base': 'rgba(46, 134, 171, 0.8)',
    'current': 'rgba(91, 140, 90, 0.8)',
    'new': 'rgba(6, 167, 125, 0.8)',
    'lost': 'rgba(199, 62, 29, 0.8)'
}

# Logging
LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)