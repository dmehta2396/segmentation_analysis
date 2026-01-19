# Segmentation Analysis Dashboard

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

Advanced customer segmentation analysis system with interactive dashboard, product analysis, cohort tracking, and risk scoring.

## 🚀 Features

- **Interactive Dashboard**: 5-tab interface with real-time analysis
- **Segment Movement Analysis**: Track customer migrations between segments
- **Product Revenue Analysis**: Product mix and segment-product matrices
- **Cohort Analysis**: Retention rates and revenue tracking by cohort
- **Risk Scoring**: Entity and segment churn risk assessment
- **Entity Search**: Individual customer journey tracking
- **Excel Export**: Comprehensive reports with multiple worksheets
- **Batch Processing**: Automated analysis for multiple time periods

## 📊 Screenshots

### Overview Dashboard
![Overview](docs/screenshots/overview.png)

### Risk Dashboard
![Risk](docs/screenshots/risk.png)

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/segmentation-analysis-dashboard.git
cd segmentation-analysis-dashboard
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Prepare data**

Place your CSV files in `data/raw/`:
- `base_seg.csv` - Base segmentation
- `curr_seg_YYYYMM.csv` - Current segmentation (one per month)
- `rev_glbl.csv` - Revenue metrics

Or generate dummy data:
```bash
python scripts/generate_dummy_data.py
```

5. **Validate data**
```bash
python scripts/validate_data.py
```

6. **Run dashboard**
```bash
python dashboards/main_app.py
```

7. **Open browser**
```
http://localhost:8050
```

## 📁 Project Structure
```
segmentation_analysis/
├── data/               # Data files
├── src/               # Source code
│   ├── analysis/      # Analysis functions
│   ├── data/          # Data loading & processing
│   ├── visualization/ # Charts & visualizations
│   └── utils/         # Utilities
├── dashboards/        # Dashboard application
│   ├── callbacks/     # Dash callbacks
│   └── layouts/       # UI layouts
└── scripts/           # Utility scripts
```

## 📝 Data Requirements

### File: `base_seg.csv`
```csv
glbl_enti_nbr,segmentation_mnth,dmnt_seg_cd
ENTITY001,202406,SEG01
```

### File: `curr_seg_YYYYMM.csv`
```csv
glbl_enti_nbr,segmentation_mnth,dmnt_seg_cd
ENTITY001,202411,SEG02
```

### File: `rev_glbl.csv`
```csv
shp_dt_yyyymm,glbl_enti_nbr,PROD_A_rev_wf,PROD_A_vol_wf,...
202305,ENTITY001,15000.50,150.5,...
```

**Note:** Column names can be customized in `src/config/settings.py`

## 🔧 Configuration

Edit `src/config/settings.py` to match your column names:
```python
SEGMENT_COLS = {
    'entity': 'your_entity_column',
    'month': 'your_month_column',
    'segment': 'your_segment_column'
}
```

## 📈 Usage

### Interactive Dashboard
1. Select comparison month
2. Click "Generate Analysis"
3. Navigate through tabs:
   - Overview
   - Product Analysis
   - Cohort Analysis
   - Risk Dashboard
   - Entity Search

### Export Reports
- Click "Export to Excel" for comprehensive analysis
- Click "Generate Risk Report" for risk assessment

### Batch Processing
```bash
python scripts/run_batch_analysis.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Your Name**
- GitHub: [@YOUR_USERNAME](https://github.com/YOUR_USERNAME)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/your-profile)

## 🙏 Acknowledgments

- Built with [Dash](https://plotly.com/dash/) by Plotly
- Visualizations powered by [Plotly](https://plotly.com/)
- UI components from [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)

## 📮 Contact

For questions or feedback, please [open an issue](https://github.com/YOUR_USERNAME/segmentation-analysis-dashboard/issues).