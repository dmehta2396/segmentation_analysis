"""
Export functions for reports and analysis
"""

import pandas as pd
import os
from datetime import datetime
from src.config.settings import EXPORT_DIR
from src.utils.dates import timer


@timer
def export_to_excel(views_dict: dict, base_month: int, current_month: int, filename: str = None) -> str:
    """
    Export all views to Excel file with multiple sheets.
    
    Args:
        views_dict: Dictionary of view names to DataFrames
        base_month: Base month
        current_month: Current month
        filename: Custom filename (optional)
        
    Returns:
        Path to exported file
    """
    print(f"Exporting {len(views_dict)} views to Excel")
    
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'segmentation_analysis_{base_month}_{current_month}_{timestamp}.xlsx'
    
    filepath = os.path.join(EXPORT_DIR, 'excel', filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Create Excel writer
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        for view_name, df in views_dict.items():
            # Clean sheet name (Excel has 31 char limit)
            sheet_name = view_name[:31]
            
            # Write DataFrame
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"  ✓ Exported to: {filepath}")
    print(f"  File size: {os.path.getsize(filepath) / 1024:.1f} KB")
    
    return filepath


@timer
def export_risk_report(risk_df: pd.DataFrame, segment_risk_df: pd.DataFrame, 
                       base_month: int, current_month: int) -> str:
    """
    Export risk analysis to Excel.
    
    Args:
        risk_df: Entity risk DataFrame
        segment_risk_df: Segment risk DataFrame
        base_month: Base month
        current_month: Current month
        
    Returns:
        Path to exported file
    """
    print("Exporting risk report")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'risk_report_{base_month}_{current_month}_{timestamp}.xlsx'
    filepath = os.path.join(EXPORT_DIR, 'excel', filename)
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Entity risks
        risk_df.to_excel(writer, sheet_name='Entity Risk Scores', index=False)
        
        # Top 100 high-risk entities
        top_risk = risk_df.head(100)
        top_risk.to_excel(writer, sheet_name='Top 100 High Risk', index=False)
        
        # Segment risks
        segment_risk_df.to_excel(writer, sheet_name='Segment Risk Analysis', index=False)
        
        # Summary
        summary_data = {
            'Metric': [
                'Total Entities Analyzed',
                'High Risk Entities',
                'Medium Risk Entities',
                'Low Risk Entities',
                'High Risk Segments',
                'Medium Risk Segments'
            ],
            'Value': [
                len(risk_df),
                len(risk_df[risk_df['risk_level'] == 'High']),
                len(risk_df[risk_df['risk_level'] == 'Medium']),
                len(risk_df[risk_df['risk_level'] == 'Low']),
                len(segment_risk_df[segment_risk_df['Risk Level'] == 'High']),
                len(segment_risk_df[segment_risk_df['Risk Level'] == 'Medium'])
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"  ✓ Exported to: {filepath}")
    
    return filepath


@timer
def export_cohort_analysis(cohort_df: pd.DataFrame, cohort_rev_df: pd.DataFrame,
                           base_month: int, current_month: int) -> str:
    """
    Export cohort analysis to Excel.
    
    Args:
        cohort_df: Cohort analysis DataFrame
        cohort_rev_df: Cohort revenue DataFrame
        base_month: Base month
        current_month: Current month
        
    Returns:
        Path to exported file
    """
    print("Exporting cohort analysis")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'cohort_analysis_{base_month}_{current_month}_{timestamp}.xlsx'
    filepath = os.path.join(EXPORT_DIR, 'excel', filename)
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        cohort_df.to_excel(writer, sheet_name='Cohort Movement', index=False)
        cohort_rev_df.to_excel(writer, sheet_name='Cohort Revenue', index=False)
    
    print(f"  ✓ Exported to: {filepath}")
    
    return filepath