"""
Generate realistic dummy datasets for segmentation analysis
"""

import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.settings import DATA_DIR

np.random.seed(42)

# Configuration
NUM_ENTITIES = 50000
BASE_MONTH = 202406
CURR_MONTHS = [202411, 202512]
METRICS_START = 202306
METRICS_END = 202512

SEGMENTS = [f'SEG{str(i).zfill(2)}' for i in range(1, 21)]
PRODUCTS = ['A1', 'A2', 'B1', 'B2', 'B3', 'C1']

SEGMENT_PROFILES = {
    'SEG01': {'size': 0.15, 'stability': 0.95, 'growth': 1.05, 'avg_rev': 50000},
    'SEG02': {'size': 0.12, 'stability': 0.93, 'growth': 1.03, 'avg_rev': 45000},
    'SEG03': {'size': 0.10, 'stability': 0.90, 'growth': 1.02, 'avg_rev': 40000},
    'SEG04': {'size': 0.08, 'stability': 0.88, 'growth': 1.08, 'avg_rev': 35000},
    'SEG05': {'size': 0.07, 'stability': 0.85, 'growth': 1.10, 'avg_rev': 30000},
    'SEG06': {'size': 0.06, 'stability': 0.82, 'growth': 0.98, 'avg_rev': 28000},
    'SEG07': {'size': 0.05, 'stability': 0.80, 'growth': 0.95, 'avg_rev': 25000},
    'SEG08': {'size': 0.05, 'stability': 0.88, 'growth': 1.01, 'avg_rev': 22000},
    'SEG09': {'size': 0.04, 'stability': 0.75, 'growth': 1.15, 'avg_rev': 20000},
    'SEG10': {'size': 0.04, 'stability': 0.78, 'growth': 1.00, 'avg_rev': 18000},
    'SEG11': {'size': 0.03, 'stability': 0.70, 'growth': 1.20, 'avg_rev': 15000},
    'SEG12': {'size': 0.03, 'stability': 0.85, 'growth': 0.97, 'avg_rev': 14000},
    'SEG13': {'size': 0.03, 'stability': 0.88, 'growth': 1.02, 'avg_rev': 12000},
    'SEG14': {'size': 0.02, 'stability': 0.65, 'growth': 1.25, 'avg_rev': 10000},
    'SEG15': {'size': 0.02, 'stability': 0.90, 'growth': 1.01, 'avg_rev': 9000},
    'SEG16': {'size': 0.02, 'stability': 0.72, 'growth': 0.92, 'avg_rev': 8000},
    'SEG17': {'size': 0.02, 'stability': 0.80, 'growth': 1.05, 'avg_rev': 7000},
    'SEG18': {'size': 0.01, 'stability': 0.60, 'growth': 1.30, 'avg_rev': 5000},
    'SEG19': {'size': 0.01, 'stability': 0.85, 'growth': 1.00, 'avg_rev': 4000},
    'SEG20': {'size': 0.01, 'stability': 0.50, 'growth': 0.85, 'avg_rev': 3000},
}


def generate_entity_ids(num_entities):
    """Generate unique entity IDs."""
    return [f'E{str(i).zfill(7)}' for i in range(1, num_entities + 1)]


def assign_base_segments(entity_ids):
    """Assign entities to segments based on segment sizes."""
    print("Assigning base segments...")
    
    segment_assignments = []
    remaining_entities = entity_ids.copy()
    
    for segment, profile in SEGMENT_PROFILES.items():
        num_in_segment = int(len(entity_ids) * profile['size'])
        selected = np.random.choice(remaining_entities, size=num_in_segment, replace=False)
        
        for entity in selected:
            segment_assignments.append({
                'glbl_enti_nbr': entity,
                'segmentation_mnth': BASE_MONTH,
                'dmnt_seg_cd': segment
            })
            remaining_entities.remove(entity)
    
    for entity in remaining_entities:
        segment_assignments.append({
            'glbl_enti_nbr': entity,
            'segmentation_mnth': BASE_MONTH,
            'dmnt_seg_cd': np.random.choice(SEGMENTS)
        })
    
    return pd.DataFrame(segment_assignments)


def generate_current_segments(base_df, current_month):
    """Generate current month segments with realistic movements."""
    print(f"Generating segments for {current_month}...")
    
    current_assignments = []
    
    for _, row in base_df.iterrows():
        entity = row['glbl_enti_nbr']
        base_segment = row['dmnt_seg_cd']
        profile = SEGMENT_PROFILES[base_segment]
        
        rand = np.random.random()
        
        if rand < profile['stability']:
            current_segment = base_segment
        elif rand < profile['stability'] + 0.03:
            continue
        else:
            seg_num = int(base_segment[3:])
            weights = np.array([0.1] * 20)
            
            start_idx = max(0, seg_num - 2)
            end_idx = min(20, seg_num + 3)
            
            for idx in range(start_idx, end_idx):
                weights[idx] = 0.15
            
            weights[seg_num - 1] = 0
            weights = weights / weights.sum()
            
            current_segment = np.random.choice(SEGMENTS, p=weights)
        
        current_assignments.append({
            'glbl_enti_nbr': entity,
            'segmentation_mnth': current_month,
            'dmnt_seg_cd': current_segment
        })
    
    # Add new entities
    growth_rate = 0.05
    num_new = int(len(base_df) * growth_rate)
    new_entity_start = len(base_df) + 1
    
    for i in range(num_new):
        new_entity = f'E{str(new_entity_start + i).zfill(7)}'
        seg_weights = np.array([SEGMENT_PROFILES[seg]['growth'] for seg in SEGMENTS])
        seg_weights = seg_weights / seg_weights.sum()
        new_segment = np.random.choice(SEGMENTS, p=seg_weights)
        
        current_assignments.append({
            'glbl_enti_nbr': new_entity,
            'segmentation_mnth': current_month,
            'dmnt_seg_cd': new_segment
        })
    
    return pd.DataFrame(current_assignments)


def generate_metrics_data(base_df, curr_dfs):
    """Generate monthly metrics for all entities."""
    print("Generating metrics data...")
    
    all_entities = set(base_df['glbl_enti_nbr'].unique())
    for curr_df in curr_dfs.values():
        all_entities.update(curr_df['glbl_enti_nbr'].unique())
    
    def get_months_range(start, end):
        months = []
        year = start // 100
        month = start % 100
        end_year = end // 100
        end_month = end % 100
        
        while (year * 100 + month) <= (end_year * 100 + end_month):
            months.append(year * 100 + month)
            month += 1
            if month > 12:
                month = 1
                year += 1
        return months
    
    months = get_months_range(METRICS_START, METRICS_END)
    metrics_data = []
    
    entity_segment_map = {}
    for _, row in base_df.iterrows():
        entity_segment_map[row['glbl_enti_nbr']] = row['dmnt_seg_cd']
    
    for entity in all_entities:
        segment = entity_segment_map.get(entity, np.random.choice(SEGMENTS))
        profile = SEGMENT_PROFILES[segment]
        base_rev = profile['avg_rev'] * np.random.uniform(0.5, 1.5)
        
        for month in months:
            month_num = month % 100
            seasonality = 1 + 0.1 * np.sin((month_num - 1) / 12 * 2 * np.pi)
            months_since_start = ((month // 100) - (METRICS_START // 100)) * 12 + (month % 100) - (METRICS_START % 100)
            growth_factor = profile['growth'] ** (months_since_start / 12)
            monthly_factor = seasonality * growth_factor * np.random.uniform(0.8, 1.2)
            
            row_data = {
                'shp_dt_yyyymm': month,
                'glbl_enti_nbr': entity
            }
            
            for product in PRODUCTS:
                if product.startswith('A'):
                    product_share = 0.40
                elif product.startswith('B'):
                    product_share = 0.35
                else:
                    product_share = 0.25
                
                product_base = base_rev * product_share / (2 if product.startswith('B') else 1)
                
                rev_wf = product_base * monthly_factor
                row_data[f'{product}_rev_wf'] = round(rev_wf, 2)
                
                rev_wof = rev_wf * np.random.uniform(0.85, 0.90)
                row_data[f'{product}_rev_wof'] = round(rev_wof, 2)
                
                vol_wf = (rev_wf / np.random.uniform(50, 150)) * np.random.uniform(0.9, 1.1)
                row_data[f'{product}_vol_wf'] = round(vol_wf, 2)
            
            metrics_data.append(row_data)
    
    return pd.DataFrame(metrics_data)


def main():
    """Generate all datasets."""
    print("="*60)
    print("GENERATING DUMMY DATASETS")
    print("="*60)
    
    entity_ids = generate_entity_ids(NUM_ENTITIES)
    print(f"\nGenerated {NUM_ENTITIES} entities")
    
    base_seg = assign_base_segments(entity_ids)
    print(f"Base segments: {len(base_seg)} entities")
    
    base_seg.to_csv(os.path.join(DATA_DIR, 'base_seg.csv'), index=False)
    print(f"✓ Saved: {DATA_DIR}/base_seg.csv")
    
    curr_dfs = {}
    for curr_month in CURR_MONTHS:
        curr_seg = generate_current_segments(base_seg, curr_month)
        curr_dfs[curr_month] = curr_seg
        
        print(f"\nCurrent segments ({curr_month}): {len(curr_seg)} entities")
        curr_seg.to_csv(os.path.join(DATA_DIR, f'curr_seg_{curr_month}.csv'), index=False)
        print(f"✓ Saved: {DATA_DIR}/curr_seg_{curr_month}.csv")
    
    metrics_df = generate_metrics_data(base_seg, curr_dfs)
    print(f"\nMetrics: {len(metrics_df)} rows")
    
    metrics_df.to_csv(os.path.join(DATA_DIR, 'rev_glbl.csv'), index=False)
    print(f"✓ Saved: {DATA_DIR}/rev_glbl.csv")
    
    print("\n" + "="*60)
    print("DATASET GENERATION COMPLETE")
    print("="*60)
    print(f"Base entities: {len(base_seg):,}")
    print(f"Current entities (202411): {len(curr_dfs[202411]):,}")
    print(f"Current entities (202512): {len(curr_dfs[202512]):,}")
    print(f"Metrics rows: {len(metrics_df):,}")
    print(f"Products: {PRODUCTS}")
    print(f"Segments: SEG01 to SEG20")
    print("\nNext step: python scripts/validate_data.py")
    print("="*60)


if __name__ == '__main__':
    main()