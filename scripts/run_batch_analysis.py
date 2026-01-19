"""
Batch analysis script - Run all analyses and export results
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from datetime import datetime

from src.data.loader import load_base_seg, load_curr_seg, load_metrics_glbl, get_available_current_months
from src.data.processor import create_snapshot
from src.analysis.summary import generate_summary_view
from src.analysis.matrix import generate_movement_matrix
from src.analysis.metrics import calculate_product_mix, calculate_segment_product_matrix
from src.analysis.cohort import identify_segment_cohorts, calculate_cohort_revenue_metrics
from src.analysis.risk import calculate_churn_risk_score, identify_at_risk_segments
from src.utils.export import export_to_excel, export_risk_report, export_cohort_analysis
from src.config.settings import SEGMENT_COLS


def run_batch_analysis():
    """Run complete analysis for all available months."""
    
    print("\n" + "="*60)
    print("BATCH ANALYSIS SCRIPT")
    print("="*60)
    
    start_time = datetime.now()
    
    # Load base data
    base_seg = load_base_seg()
    metrics_glbl = load_metrics_glbl()
    available_months = get_available_current_months()
    
    base_month = base_seg[SEGMENT_COLS['month']].iloc[0]
    
    print(f"\nBase month: {base_month}")
    print(f"Will analyze {len(available_months)} comparison months: {available_months}")
    
    results_summary = []
    
    for curr_month in available_months:
        print(f"\n{'='*60}")
        print(f"ANALYZING: {base_month} vs {curr_month}")
        print(f"{'='*60}")
        
        try:
            # Load current month data
            curr_seg = load_curr_seg(curr_month)
            
            # Create snapshot
            snapshot = create_snapshot(base_seg, curr_seg, metrics_glbl)
            
            # Generate all views
            print("\nGenerating analysis views...")
            views = {}
            
            views['Count Summary'] = generate_summary_view(snapshot, 'count')
            views['Count Matrix'] = generate_movement_matrix(snapshot, 'count')
            views['Product Mix'] = calculate_product_mix(snapshot)
            views['Segment-Product Matrix'] = calculate_segment_product_matrix(snapshot)
            
            # Cohort analysis
            print("\nRunning cohort analysis...")
            cohort_df = identify_segment_cohorts(snapshot)
            cohort_rev_df = calculate_cohort_revenue_metrics(snapshot)
            views['Cohort Analysis'] = cohort_df
            views['Cohort Revenue'] = cohort_rev_df
            
            # Risk analysis
            print("\nRunning risk analysis...")
            entity_risk_df = calculate_churn_risk_score(snapshot)
            segment_risk_df = identify_at_risk_segments(snapshot)
            views['Entity Risk Scores'] = entity_risk_df.head(100)
            views['Segment Risk Analysis'] = segment_risk_df
            
            # Export to Excel
            print("\nExporting results...")
            excel_path = export_to_excel(views, base_month, curr_month)
            
            # Export separate risk report
            risk_path = export_risk_report(entity_risk_df, segment_risk_df, base_month, curr_month)
            
            # Export cohort analysis
            cohort_path = export_cohort_analysis(cohort_df, cohort_rev_df, base_month, curr_month)
            
            results_summary.append({
                'Base Month': base_month,
                'Current Month': curr_month,
                'Entities': len(snapshot),
                'High Risk Entities': len(entity_risk_df[entity_risk_df['risk_level'] == 'High']),
                'Excel Report': excel_path,
                'Risk Report': risk_path,
                'Cohort Report': cohort_path,
                'Status': 'Success'
            })
            
            print(f"\n✓ Analysis complete for {curr_month}")
            
        except Exception as e:
            print(f"\n✗ Analysis failed for {curr_month}: {str(e)}")
            import traceback
            traceback.print_exc()
            
            results_summary.append({
                'Base Month': base_month,
                'Current Month': curr_month,
                'Entities': 0,
                'High Risk Entities': 0,
                'Excel Report': 'Failed',
                'Risk Report': 'Failed',
                'Cohort Report': 'Failed',
                'Status': f'Error: {str(e)}'
            })
    
    # Create summary report
    print("\n" + "="*60)
    print("BATCH ANALYSIS SUMMARY")
    print("="*60)
    
    summary_df = pd.DataFrame(results_summary)
    print(summary_df.to_string(index=False))
    
    # Export summary
    summary_path = os.path.join('data/exports/excel', f'batch_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
    summary_df.to_excel(summary_path, index=False)
    print(f"\n✓ Summary exported to: {summary_path}")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n⏱️  Total batch analysis time: {duration:.2f} seconds ({duration/60:.1f} minutes)")
    print("="*60)


if __name__ == '__main__':
    run_batch_analysis()