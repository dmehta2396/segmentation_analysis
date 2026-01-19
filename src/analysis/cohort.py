"""
Cohort analysis functions
"""

import pandas as pd
from src.utils.dates import timer


@timer
def identify_segment_cohorts(snapshot: pd.DataFrame) -> pd.DataFrame:
    """
    Group entities into cohorts based on their base segment.
    
    Args:
        snapshot: Snapshot dataframe
        
    Returns:
        DataFrame with cohort analysis
    """
    print("Identifying segment cohorts")
    
    cohorts = []
    
    base_segments = sorted(snapshot['base_segment'].dropna().unique())
    
    for base_seg in base_segments:
        cohort_data = snapshot[snapshot['base_segment'] == base_seg]
        
        cohort = {
            'Base Segment': base_seg,
            'Cohort Size': len(cohort_data),
            'Retained': len(cohort_data[cohort_data['status'] == 'Retained']),
            'Moved Up': 0,
            'Moved Down': 0,
            'Churned': len(cohort_data[cohort_data['status'] == 'Lost (System)']),
        }
        
        # Calculate moved up/down based on segment number
        base_num = int(base_seg[3:])
        
        for _, row in cohort_data[cohort_data['status'] == 'Moved Internal'].iterrows():
            curr_seg = row['current_segment']
            if pd.notna(curr_seg):
                curr_num = int(curr_seg[3:])
                if curr_num < base_num:
                    cohort['Moved Up'] += 1
                else:
                    cohort['Moved Down'] += 1
        
        # Calculate percentages
        cohort['Retention Rate'] = (cohort['Retained'] / cohort['Cohort Size'] * 100) if cohort['Cohort Size'] > 0 else 0
        cohort['Churn Rate'] = (cohort['Churned'] / cohort['Cohort Size'] * 100) if cohort['Cohort Size'] > 0 else 0
        
        cohorts.append(cohort)
    
    cohort_df = pd.DataFrame(cohorts)
    
    print(f"  Created {len(cohorts)} cohorts")
    print(f"  Average retention rate: {cohort_df['Retention Rate'].mean():.1f}%")
    
    return cohort_df


@timer
def calculate_cohort_revenue_metrics(snapshot: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate revenue metrics by cohort.
    
    Args:
        snapshot: Snapshot dataframe
        
    Returns:
        DataFrame with cohort revenue analysis
    """
    print("Calculating cohort revenue metrics")
    
    base_segments = sorted(snapshot['base_segment'].dropna().unique())
    
    # Get revenue columns
    base_rev_cols = [col for col in snapshot.columns if col.startswith('base_') and '_rev_wf' in col]
    curr_rev_cols = [col for col in snapshot.columns if col.startswith('current_') and '_rev_wf' in col]
    
    cohort_revenues = []
    
    for base_seg in base_segments:
        cohort_data = snapshot[snapshot['base_segment'] == base_seg]
        
        base_revenue = sum(cohort_data[col].sum() for col in base_rev_cols)
        current_revenue = sum(cohort_data[col].sum() for col in curr_rev_cols)
        
        cohort_rev = {
            'Cohort': base_seg,
            'Entities': len(cohort_data),
            'Base Revenue': base_revenue,
            'Current Revenue': current_revenue,
            'Revenue Change': current_revenue - base_revenue,
            'Revenue Change %': ((current_revenue - base_revenue) / base_revenue * 100) if base_revenue > 0 else 0,
            'Avg Revenue per Entity (Base)': base_revenue / len(cohort_data) if len(cohort_data) > 0 else 0,
            'Avg Revenue per Entity (Current)': current_revenue / len(cohort_data) if len(cohort_data) > 0 else 0,
        }
        
        cohort_revenues.append(cohort_rev)
    
    cohort_df = pd.DataFrame(cohort_revenues)
    
    print(f"  Total base revenue: ${cohort_df['Base Revenue'].sum():,.2f}")
    print(f"  Total current revenue: ${cohort_df['Current Revenue'].sum():,.2f}")
    
    return cohort_df