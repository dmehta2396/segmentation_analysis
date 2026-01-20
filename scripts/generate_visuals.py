"""
Generate individual visualizations and export as images
No dashboard - just create PNG/HTML files
OPTIMIZED FOR LARGE DATASETS
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import gc  # Garbage collector
from datetime import datetime

from src.data.loader import load_base_seg, load_curr_seg, load_metrics_glbl, get_available_current_months
from src.data.processor import create_snapshot
from src.analysis.summary import generate_summary_view
from src.analysis.matrix import generate_movement_matrix
from src.analysis.sankey import generate_sankey_data
from src.analysis.metrics import calculate_product_mix, calculate_segment_product_matrix
from src.analysis.cohort import identify_segment_cohorts, calculate_cohort_revenue_metrics
from src.analysis.risk import calculate_churn_risk_score, identify_at_risk_segments
from src.visualization.charts import (
    create_comparison_chart,
    create_summary_bar_chart,
    create_movement_heatmap,
    create_sankey_diagram
)
from src.visualization.advanced_charts import (
    create_product_mix_pie,
    create_segment_product_heatmap,
    create_cohort_retention_chart,
    create_cohort_revenue_waterfall,
    create_risk_scatter,
    create_segment_risk_bars
)
from src.config.settings import SEGMENT_COLS, EXPORT_DIR


def sample_large_data(base_seg, curr_seg, metrics_glbl, sample_fraction=0.1):
    """Sample data if too large."""
    MAX_ENTITIES = 50000
    
    if len(base_seg) > MAX_ENTITIES:
        print(f"\nLarge dataset detected ({len(base_seg):,} entities)")
        print(f"Sampling {sample_fraction*100}% for memory efficiency...")
        
        base_seg = base_seg.sample(frac=sample_fraction, random_state=42)
        curr_seg = curr_seg.sample(frac=sample_fraction, random_state=42)
        
        sampled_entities = set(base_seg[SEGMENT_COLS['entity']]) | set(curr_seg[SEGMENT_COLS['entity']])
        metrics_glbl = metrics_glbl[metrics_glbl['glbl_enti_nbr'].isin(sampled_entities)]
        
        print(f"Sampled to: {len(base_seg):,} base, {len(curr_seg):,} current entities")
    
    return base_seg, curr_seg, metrics_glbl


def save_figure(fig, filename, output_dir, step_num, total_steps):
    """Save figure as HTML with progress indicator."""
    html_path = os.path.join(output_dir, f"{filename}.html")
    
    print(f"    [{step_num}/{total_steps}] Saving {filename}...", end='', flush=True)
    
    # Configure for better performance
    fig.write_html(
        html_path,
        config={'displayModeBar': False},
        include_plotlyjs='cdn'  # Use CDN instead of embedding (smaller files)
    )
    
    print(" ✓")
    
    # Clear memory
    del fig
    gc.collect()


def generate_all_visuals(base_month, current_month):
    """Generate all visualizations for selected months."""
    
    print("\n" + "="*60)
    print(f"GENERATING VISUALIZATIONS: {base_month} vs {current_month}")
    print("="*60)
    
    # Create output directory with explicit path
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    folder_name = f'visuals_{base_month}_{current_month}_{timestamp}'
    output_dir = os.path.abspath(os.path.join('data', 'exports', folder_name))
    
    # CREATE DIRECTORY
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nOutput directory: {output_dir}")
    
    total_steps = 14  # Total number of visualizations + tables
    current_step = 0
    
    try:
        # Load data
        print("\n" + "="*60)
        print("STEP 1: LOADING DATA")
        print("="*60)
        base_seg = load_base_seg()
        curr_seg = load_curr_seg(current_month)
        metrics_glbl = load_metrics_glbl()
        
        # Sample if needed
        base_seg, curr_seg, metrics_glbl = sample_large_data(
            base_seg, curr_seg, metrics_glbl, sample_fraction=0.1
        )
        
        # Create snapshot
        print("\n" + "="*60)
        print("STEP 2: CREATING SNAPSHOT")
        print("="*60)
        snapshot = create_snapshot(base_seg, curr_seg, metrics_glbl)
        
        # Clear memory
        del base_seg, curr_seg, metrics_glbl
        gc.collect()
        
        # Generate summary data
        print("\n" + "="*60)
        print("STEP 3: GENERATING ANALYSIS DATA")
        print("="*60)
        print("  Calculating summary view...")
        summary_df = generate_summary_view(snapshot, 'count')
        
        print("  Calculating movement matrix...")
        matrix_df = generate_movement_matrix(snapshot, 'count')
        
        print("  Calculating sankey data...")
        sankey_data = generate_sankey_data(snapshot, 'count')
        
        # Save tables as Excel
        print("\n" + "="*60)
        print("STEP 4: EXPORTING DATA TABLES")
        print("="*60)
        
        current_step += 1
        print(f"  [{current_step}/{total_steps}] Saving main tables...")
        excel_path = os.path.join(output_dir, 'tables.xlsx')
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            matrix_df.to_excel(writer, sheet_name='Matrix', index=False)
        print("    ✓ tables.xlsx")
        
        # Generate visualizations
        print("\n" + "="*60)
        print("STEP 5: CREATING VISUALIZATIONS (10 charts)")
        print("="*60)
        print("\n  OVERVIEW CHARTS:")
        
        current_step += 1
        print(f"    [{current_step}/{total_steps}] Base vs Current comparison...", end='', flush=True)
        fig1 = create_comparison_chart(summary_df, "COUNT")
        save_figure(fig1, "01_base_vs_current", output_dir, current_step, total_steps)
        
        current_step += 1
        print(f"    [{current_step}/{total_steps}] Sankey flow diagram (this takes longer)...", end='', flush=True)
        fig2 = create_sankey_diagram(sankey_data, "COUNT")
        save_figure(fig2, "02_sankey_flow", output_dir, current_step, total_steps)
        
        current_step += 1
        print(f"    [{current_step}/{total_steps}] Movement breakdown...", end='', flush=True)
        fig3 = create_summary_bar_chart(summary_df, "COUNT")
        save_figure(fig3, "03_movement_breakdown", output_dir, current_step, total_steps)
        
        current_step += 1
        print(f"    [{current_step}/{total_steps}] Movement heatmap...", end='', flush=True)
        fig4 = create_movement_heatmap(matrix_df, "COUNT")
        save_figure(fig4, "04_movement_heatmap", output_dir, current_step, total_steps)
        
        # Product Analysis
        print("\n  PRODUCT ANALYSIS:")
        print("    Calculating product metrics...")
        product_mix = calculate_product_mix(snapshot)
        seg_product_matrix = calculate_segment_product_matrix(snapshot)
        
        if len(product_mix) > 0:
            current_step += 1
            print(f"    [{current_step}/{total_steps}] Product mix pie chart...", end='', flush=True)
            fig5 = create_product_mix_pie(product_mix, "Revenue")
            save_figure(fig5, "05_product_mix", output_dir, current_step, total_steps)
            
            current_step += 1
            print(f"    [{current_step}/{total_steps}] Segment-product heatmap...", end='', flush=True)
            fig6 = create_segment_product_heatmap(seg_product_matrix)
            save_figure(fig6, "06_segment_product_matrix", output_dir, current_step, total_steps)
            
            # Save product tables
            current_step += 1
            print(f"    [{current_step}/{total_steps}] Product analysis tables...")
            product_excel = os.path.join(output_dir, 'product_analysis.xlsx')
            with pd.ExcelWriter(product_excel, engine='openpyxl') as writer:
                product_mix.to_excel(writer, sheet_name='Product Mix', index=False)
                seg_product_matrix.to_excel(writer, sheet_name='Segment-Product', index=False)
            print("      ✓ product_analysis.xlsx")
        else:
            print("    No product data found - skipping product charts")
            current_step += 3  # Skip 3 steps
        
        # Cohort Analysis
        print("\n  COHORT ANALYSIS:")
        print("    Calculating cohort metrics...")
        cohort_df = identify_segment_cohorts(snapshot)
        cohort_rev_df = calculate_cohort_revenue_metrics(snapshot)
        
        current_step += 1
        print(f"    [{current_step}/{total_steps}] Cohort retention chart...", end='', flush=True)
        fig7 = create_cohort_retention_chart(cohort_df)
        save_figure(fig7, "07_cohort_retention", output_dir, current_step, total_steps)
        
        current_step += 1
        print(f"    [{current_step}/{total_steps}] Cohort revenue waterfall...", end='', flush=True)
        fig8 = create_cohort_revenue_waterfall(cohort_rev_df)
        save_figure(fig8, "08_cohort_revenue", output_dir, current_step, total_steps)
        
        # Save cohort tables
        current_step += 1
        print(f"    [{current_step}/{total_steps}] Cohort analysis tables...")
        cohort_excel = os.path.join(output_dir, 'cohort_analysis.xlsx')
        with pd.ExcelWriter(cohort_excel, engine='openpyxl') as writer:
            cohort_df.to_excel(writer, sheet_name='Cohort Movement', index=False)
            cohort_rev_df.to_excel(writer, sheet_name='Cohort Revenue', index=False)
        print("      ✓ cohort_analysis.xlsx")
        
        # Risk Analysis
        print("\n  RISK ANALYSIS:")
        print("    Calculating risk scores...")
        entity_risk_df = calculate_churn_risk_score(snapshot)
        segment_risk_df = identify_at_risk_segments(snapshot)
        
        current_step += 1
        print(f"    [{current_step}/{total_steps}] Risk scatter plot...", end='', flush=True)
        fig9 = create_risk_scatter(entity_risk_df)
        save_figure(fig9, "09_risk_scatter", output_dir, current_step, total_steps)
        
        current_step += 1
        print(f"    [{current_step}/{total_steps}] Segment risk bars...", end='', flush=True)
        fig10 = create_segment_risk_bars(segment_risk_df)
        save_figure(fig10, "10_segment_risk", output_dir, current_step, total_steps)
        
        # Save risk tables
        current_step += 1
        print(f"    [{current_step}/{total_steps}] Risk analysis tables...")
        risk_excel = os.path.join(output_dir, 'risk_analysis.xlsx')
        with pd.ExcelWriter(risk_excel, engine='openpyxl') as writer:
            entity_risk_df.head(100).to_excel(writer, sheet_name='Top 100 High Risk', index=False)
            segment_risk_df.to_excel(writer, sheet_name='Segment Risk', index=False)
        print("      ✓ risk_analysis.xlsx")
        
        # Create summary report
        print("\n" + "="*60)
        print("STEP 6: CREATING SUMMARY REPORT")
        print("="*60)
        create_summary_report(output_dir, base_month, current_month, summary_df, 
                            entity_risk_df, cohort_df)
        
        print("\n" + "="*60)
        print("✅ ALL VISUALIZATIONS GENERATED SUCCESSFULLY!")
        print("="*60)
        print(f"\nOutput folder: {output_dir}")
        print(f"\nGenerated files:")
        print(f"  - 10 interactive HTML charts")
        print(f"  - 4 Excel data files")
        print(f"  - 1 Summary report")
        print("\nYou can:")
        print(f"  1. Open HTML files in browser for interactive charts")
        print(f"  2. Open Excel files for data tables")
        print(f"  3. Share the entire folder")
        print("="*60)
        
        return output_dir
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def create_summary_report(output_dir, base_month, current_month, summary_df, risk_df, cohort_df):
    """Create a text summary report."""
    
    report_path = os.path.join(output_dir, 'SUMMARY_REPORT.txt')
    
    # FIX: Use UTF-8 encoding to support arrow characters
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("SEGMENTATION ANALYSIS SUMMARY REPORT\n")
        f.write("="*60 + "\n\n")
        
        f.write(f"Analysis Period: {base_month} -> {current_month}\n")  # Changed arrow
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("="*60 + "\n")
        f.write("OVERVIEW\n")
        f.write("="*60 + "\n\n")
        
        totals = summary_df[summary_df['Segment'] == 'TOTAL'].iloc[0]
        f.write(f"Total Entities (Base):     {totals['Base']:,.0f}\n")
        f.write(f"Total Entities (Current):  {totals['Current']:,.0f}\n")
        f.write(f"Net Change:                {totals['Net Change']:,.0f}\n")
        f.write(f"Retained:                  {totals['Retained']:,.0f}\n")
        f.write(f"New (System):              {totals['New (System)']:,.0f}\n")
        f.write(f"Lost (System):             {totals['Lost (System)']:,.0f}\n\n")
        
        f.write("="*60 + "\n")
        f.write("RISK ANALYSIS\n")
        f.write("="*60 + "\n\n")
        
        high_risk = len(risk_df[risk_df['risk_level'] == 'High'])
        medium_risk = len(risk_df[risk_df['risk_level'] == 'Medium'])
        low_risk = len(risk_df[risk_df['risk_level'] == 'Low'])
        
        f.write(f"High Risk Entities:    {high_risk:,} ({high_risk/len(risk_df)*100:.1f}%)\n")
        f.write(f"Medium Risk Entities:  {medium_risk:,} ({medium_risk/len(risk_df)*100:.1f}%)\n")
        f.write(f"Low Risk Entities:     {low_risk:,} ({low_risk/len(risk_df)*100:.1f}%)\n\n")
        
        f.write("="*60 + "\n")
        f.write("COHORT SUMMARY\n")
        f.write("="*60 + "\n\n")
        
        avg_retention = cohort_df['Retention Rate'].mean()
        avg_churn = cohort_df['Churn Rate'].mean()
        
        f.write(f"Average Retention Rate: {avg_retention:.1f}%\n")
        f.write(f"Average Churn Rate:     {avg_churn:.1f}%\n\n")
        
        f.write("="*60 + "\n")
        f.write("FILES GENERATED\n")
        f.write("="*60 + "\n\n")
        
        f.write("Charts (HTML - interactive):\n")
        f.write("  01_base_vs_current.html\n")
        f.write("  02_sankey_flow.html\n")
        f.write("  03_movement_breakdown.html\n")
        f.write("  04_movement_heatmap.html\n")
        f.write("  05_product_mix.html\n")
        f.write("  06_segment_product_matrix.html\n")
        f.write("  07_cohort_retention.html\n")
        f.write("  08_cohort_revenue.html\n")
        f.write("  09_risk_scatter.html\n")
        f.write("  10_segment_risk.html\n\n")
        
        f.write("Data Tables (Excel):\n")
        f.write("  tables.xlsx\n")
        f.write("  product_analysis.xlsx\n")
        f.write("  cohort_analysis.xlsx\n")
        f.write("  risk_analysis.xlsx\n\n")
        
        f.write("="*60 + "\n")
    
    print(f"  ✓ SUMMARY_REPORT.txt")


def main():
    """Main function - interactive mode."""
    
    print("\n" + "="*60)
    print("SEGMENTATION ANALYSIS - VISUAL GENERATOR")
    print("="*60)
    
    # Load base data to get base month
    print("\nLoading base data...")
    base_seg = load_base_seg()
    base_month = base_seg[SEGMENT_COLS['month']].iloc[0]
    
    print(f"\nBase month: {base_month}")
    
    # Get available months
    available_months = get_available_current_months()
    
    if len(available_months) == 0:
        print("\n❌ No comparison months found!")
        print("Please add curr_seg_YYYYMM.csv files to data/raw/")
        return
    
    print(f"\nAvailable comparison months:")
    for i, month in enumerate(available_months, 1):
        print(f"  {i}. {month}")
    
    # Get user choice
    print("\nSelect a comparison month:")
    choice = input(f"Enter number (1-{len(available_months)}): ").strip()
    
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(available_months):
            raise ValueError()
        
        selected_month = available_months[idx]
        
        # Generate visuals
        start_time = datetime.now()
        output_dir = generate_all_visuals(base_month, selected_month)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        if output_dir:
            print(f"\n⏱️  Total time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
            
            # Open folder
            print("\nOpening output folder...")
            try:
                os.startfile(output_dir)  # Windows
            except:
                print(f"Please manually open: {output_dir}")
        
    except (ValueError, IndexError):
        print("\n❌ Invalid selection!")
        return
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        return


if __name__ == '__main__':
    main()