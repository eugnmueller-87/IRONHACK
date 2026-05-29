# LAB 9 — In God We Trust, Everyone Else Bring the Data

Statistical analysis of marketing channel performance to drive $500K budget allocation.

## File Map

```
lab_statistical_analysis_eugen_mueller/
│
├── data/
│   └── marketing_data.csv          # 630 rows × 11 cols — 90 days × 7 channels
│
├── outputs/                        # All generated charts and results CSVs
│   ├── group_metrics_overview.png
│   ├── group_distributions.png
│   ├── metric_comparison_heatmap.png
│   ├── rate_comparison.png
│   ├── correction_comparison.png
│   ├── power_analysis_cpa.png
│   ├── cpa_comparisons.csv
│   └── fisher_comparisons.csv
│
├── generate_dataset.py             # Generates marketing_data.csv (run once)
├── data_exploration.ipynb          # Part 1 — load, explore, metrics, visualizations
├── statistical_analysis.ipynb      # Parts 2-3 — t-tests, Fisher's, corrections
├── power_analysis.py               # Part 4 — power curves, sample size planning
├── executive_memo.md               # Part 5 — business recommendations
└── reflection.md                   # Post-analysis reflection
```

## How to Run

**Requires:** Python 3.10+, anaconda3 environment (or: `pip install pandas numpy scipy matplotlib seaborn`)

```bash
# 1. Generate dataset
python generate_dataset.py

# 2. Open notebooks in Jupyter and run all cells top-to-bottom
jupyter notebook data_exploration.ipynb
jupyter notebook statistical_analysis.ipynb

# 3. Run power analysis (takes ~30 seconds)
python power_analysis.py
```

Run in order: `generate_dataset.py` → `data_exploration.ipynb` → `statistical_analysis.ipynb` → `power_analysis.py`.  
`statistical_analysis.ipynb` writes `outputs/cpa_comparisons.csv` which `power_analysis.py` reads.

## Dataset

**Name:** Digital Marketing Channel Performance (synthetic)  
**Source:** Generated via `generate_dataset.py` — mirrors Kaggle "Marketing Campaign Performance" structure  
**Period:** Oct 1 – Dec 29, 2024 (90 days)  
**Channels:** Paid Search, Paid Social, Display, Email, Affiliate, SEO Organic, Video  
**Metrics:** impressions, clicks, conversions, cost, revenue, CTR, conversion rate, CPA, ROAS  

## Key Findings (TLDR)

- Email dominates: $0.77 CPA vs $52 for Display — 67x more efficient
- All 14 paid-channel CPA differences are statistically significant after FDR correction
- All 21 conversion rate differences are significant after FDR correction
- Recommended: shift budget from Display/Video to Email + Affiliate + SEO investment
- 90 days of data is adequate to detect ≥10% CPA differences with 80% power

See `executive_memo.md` for full analysis and budget allocation table.
