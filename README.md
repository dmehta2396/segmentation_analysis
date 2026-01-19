# Segmentation Analysis Dashboard

Comprehensive customer segmentation analysis with movement tracking, revenue analysis, and risk scoring.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Place your data files in `data/raw/`:
   - `base_seg.csv`
   - `curr_seg_YYYYMM.csv` (one per month)
   - `rev_glbl.csv`

3. Validate data:
```bash
python scripts/validate_data.py
```

4. Run dashboard:
```bash
python dashboards/main_app.py
```

5. Open browser: http://localhost:8050

## Data Requirements

### base_seg.csv
- glbl_enti_nbr (entity ID)
- segmentation_mnth (YYYYMM format)
- dmnt_seg_cd (segment code)

### curr_seg_YYYYMM.csv
- Same columns as base_seg.csv
- Create one file per comparison month

### rev_glbl.csv
- glbl_enti_nbr (entity ID)
- shp_dt_yyyymm (YYYYMM format)
- Product metric columns (auto-detected)

## Configuration

Edit column names in `src/config/settings.py` if your columns are named differently.

## Features

- Segment movement analysis
- Product revenue analysis
- Cohort analysis
- Risk scoring
- Entity search
- Excel export
- Batch processing