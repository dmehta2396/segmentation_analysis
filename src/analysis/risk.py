"""
Risk analysis and prediction functions
"""

import pandas as pd
import numpy as np
from src.utils.dates import timer


@timer
def calculate_churn_risk_score(snapshot: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate churn risk score for entities in current month.
    
    Args:
        snapshot: Snapshot dataframe
        
    Returns:
        DataFrame with entities and their risk scores
    """
    print("Calculating churn risk scores")
    
    # Filter to entities in current month
    current_entities = snapshot[snapshot['current_segment'].notna()].copy()
    
    # Get revenue columns
    base_rev_cols = [col for col in snapshot.columns if col.startswith('base_') and '_rev_wf' in col]
    curr_rev_cols = [col for col in snapshot.columns if col.startswith('current_') and '_rev_wf' in col]
    
    risk_scores = []
    
    for _, entity in current_entities.iterrows():
        score = 0
        risk_factors = []
        
        # Factor 1: Revenue decline (0-40 points)
        base_rev = sum(entity[col] for col in base_rev_cols if col in entity.index)
        curr_rev = sum(entity[col] for col in curr_rev_cols if col in entity.index)
        
        if base_rev > 0:
            rev_change_pct = ((curr_rev - base_rev) / base_rev) * 100
            if rev_change_pct < -20:
                score += 40
                risk_factors.append(f"Revenue declined {rev_change_pct:.1f}%")
            elif rev_change_pct < -10:
                score += 25
                risk_factors.append(f"Revenue declined {rev_change_pct:.1f}%")
            elif rev_change_pct < 0:
                score += 10
                risk_factors.append(f"Revenue declined {rev_change_pct:.1f}%")
        
        # Factor 2: Low revenue (0-20 points)
        if curr_rev < 5000:
            score += 20
            risk_factors.append("Low revenue")
        elif curr_rev < 10000:
            score += 10
            risk_factors.append("Below average revenue")
        
        # Factor 3: In declining segments (0-20 points)
        curr_seg = entity['current_segment']
        if pd.notna(curr_seg):
            seg_num = int(curr_seg[3:])
            if seg_num >= 16:
                score += 20
                risk_factors.append("In bottom-tier segment")
            elif seg_num >= 11:
                score += 10
                risk_factors.append("In lower-tier segment")
        
        # Factor 4: Recently moved segments (0-20 points)
        if entity['status'] == 'Moved Internal':
            base_seg = entity['base_segment']
            if pd.notna(base_seg) and pd.notna(curr_seg):
                base_num = int(base_seg[3:])
                curr_num = int(curr_seg[3:])
                if curr_num > base_num:  # Moved down
                    score += 20
                    risk_factors.append("Moved to lower segment")
        
        # Determine risk level
        if score >= 60:
            risk_level = 'High'
        elif score >= 30:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        risk_scores.append({
            'entity': entity['entity'],
            'current_segment': curr_seg,
            'current_revenue': curr_rev,
            'risk_score': score,
            'risk_level': risk_level,
            'risk_factors': ', '.join(risk_factors) if risk_factors else 'None'
        })
    
    risk_df = pd.DataFrame(risk_scores)
    risk_df = risk_df.sort_values('risk_score', ascending=False).reset_index(drop=True)
    
    high_risk = len(risk_df[risk_df['risk_level'] == 'High'])
    medium_risk = len(risk_df[risk_df['risk_level'] == 'Medium'])
    low_risk = len(risk_df[risk_df['risk_level'] == 'Low'])
    
    print(f"  High risk: {high_risk} entities")
    print(f"  Medium risk: {medium_risk} entities")
    print(f"  Low risk: {low_risk} entities")
    
    return risk_df


@timer
def identify_at_risk_segments(snapshot: pd.DataFrame) -> pd.DataFrame:
    """
    Identify segments with high churn risk.
    
    Args:
        snapshot: Snapshot dataframe
        
    Returns:
        DataFrame with segment risk analysis
    """
    print("Identifying at-risk segments")
    
    segments = sorted(snapshot['current_segment'].dropna().unique())
    
    segment_risks = []
    
    for segment in segments:
        seg_data = snapshot[snapshot['current_segment'] == segment]
        
        # Calculate churn rate
        base_in_segment = snapshot[snapshot['base_segment'] == segment]
        churned = len(base_in_segment[base_in_segment['status'] == 'Lost (System)'])
        churn_rate = (churned / len(base_in_segment) * 100) if len(base_in_segment) > 0 else 0
        
        # Calculate revenue decline
        base_rev_cols = [col for col in snapshot.columns if col.startswith('base_') and '_rev_wf' in col]
        curr_rev_cols = [col for col in snapshot.columns if col.startswith('current_') and '_rev_wf' in col]
        
        base_seg_rev = sum(base_in_segment[col].sum() for col in base_rev_cols)
        curr_seg_rev = sum(seg_data[col].sum() for col in curr_rev_cols)
        rev_change_pct = ((curr_seg_rev - base_seg_rev) / base_seg_rev * 100) if base_seg_rev > 0 else 0
        
        # Calculate risk score
        risk_score = 0
        if churn_rate > 10:
            risk_score += 40
        elif churn_rate > 5:
            risk_score += 20
        
        if rev_change_pct < -15:
            risk_score += 40
        elif rev_change_pct < -5:
            risk_score += 20
        
        seg_num = int(segment[3:])
        if seg_num >= 15:
            risk_score += 20
        
        risk_level = 'High' if risk_score >= 60 else 'Medium' if risk_score >= 30 else 'Low'
        
        segment_risks.append({
            'Segment': segment,
            'Current Size': len(seg_data),
            'Churn Rate %': round(churn_rate, 2),
            'Revenue Change %': round(rev_change_pct, 2),
            'Risk Score': risk_score,
            'Risk Level': risk_level
        })
    
    risk_df = pd.DataFrame(segment_risks)
    risk_df = risk_df.sort_values('Risk Score', ascending=False).reset_index(drop=True)
    
    print(f"  High risk segments: {len(risk_df[risk_df['Risk Level'] == 'High'])}")
    
    return risk_df