"""
Validate data files before running dashboard
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import glob
from src.config.settings import DATA_DIR, SEGMENT_COLS, METRICS_COLS


def validate_file(filepath, required_cols, file_type):
    """Validate a single file."""
    print(f"\n{'='*60}")
    print(f"Validating: {os.path.basename(filepath)}")
    print(f"{'='*60}")
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    try:
        df = pd.read_csv(filepath, nrows=1000)
        print(f"✓ File loaded successfully")
        
        # Check columns
        missing = set(required_cols) - set(df.columns)
        if missing:
            print(f"❌ Missing columns: {missing}")
            print(f"   Available: {list(df.columns)}")
            return False
        
        print(f"✓ All required columns present: {required_cols}")
        
        # Full file stats
        df_full = pd.read_csv(filepath)
        print(f"✓ Total rows: {len(df_full):,}")
        
        if file_type == 'segment':
            print(f"✓ Unique entities: {df_full[required_cols[0]].nunique():,}")
            print(f"✓ Segments: {sorted(df_full[required_cols[2]].unique())}")
        elif file_type == 'metrics':
            print(f"✓ Unique entities: {df_full[required_cols[0]].nunique():,}")
            print(f"✓ Month range: {df_full[required_cols[1]].min()} - {df_full[required_cols[1]].max()}")
            metric_cols = [c for c in df.columns if c not in required_cols]
            print(f"✓ Metric columns detected: {len(metric_cols)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    print("\n" + "="*60)
    print("DATA VALIDATION")
    print("="*60)
    
    results = []
    
    # 1. Validate base_seg.csv
    base_path = os.path.join(DATA_DIR, 'base_seg.csv')
    seg_cols = [SEGMENT_COLS['entity'], SEGMENT_COLS['month'], SEGMENT_COLS['segment']]
    results.append(validate_file(base_path, seg_cols, 'segment'))
    
    # 2. Validate curr_seg files
    curr_files = glob.glob(os.path.join(DATA_DIR, 'curr_seg_*.csv'))
    if not curr_files:
        print(f"\n❌ No curr_seg_*.csv files found in {DATA_DIR}")
        results.append(False)
    else:
        print(f"\n✓ Found {len(curr_files)} current segmentation files")
        for f in curr_files:
            results.append(validate_file(f, seg_cols, 'segment'))
    
    # 3. Validate rev_glbl.csv
    metrics_path = os.path.join(DATA_DIR, 'rev_glbl.csv')
    metrics_cols = [METRICS_COLS['entity'], METRICS_COLS['month']]
    results.append(validate_file(metrics_path, metrics_cols, 'metrics'))
    
    # Summary
    print("\n" + "="*60)
    if all(results):
        print("✅ ALL VALIDATION PASSED - Ready to run dashboard!")
        print("\nNext steps:")
        print("  python dashboards/main_app.py")
    else:
        print("❌ VALIDATION FAILED - Fix errors above")
        print("\nCommon fixes:")
        print("  1. Check column names in src/config/settings.py")
        print("  2. Verify date format is YYYYMM (not YYYY-MM-DD)")
        print("  3. Ensure entity IDs match across all files")
    print("="*60 + "\n")
    
    return all(results)


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)