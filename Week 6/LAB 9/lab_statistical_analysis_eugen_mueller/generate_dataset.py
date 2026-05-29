"""
Generate a realistic synthetic marketing channel performance dataset.

Mirrors the structure of Kaggle's "Digital Marketing Campaign Performance" datasets.
90 days of daily observations across 7 channels — realistic means, noise, and
seasonal patterns so stats tests produce non-trivial, interesting results.
"""

import numpy as np
import pandas as pd

np.random.seed(42)

CHANNELS = {
    "Paid_Search":   {"impressions_mean": 45_000, "ctr": 0.045, "cvr": 0.038, "cpc": 1.20, "aov": 82},
    "Paid_Social":   {"impressions_mean": 90_000, "ctr": 0.018, "cvr": 0.021, "cpc": 0.95, "aov": 71},
    "Display":       {"impressions_mean": 200_000, "ctr": 0.006, "cvr": 0.008, "cpc": 0.40, "aov": 65},
    "Email":         {"impressions_mean": 30_000, "ctr": 0.110, "cvr": 0.065, "cpc": 0.05, "aov": 95},
    "Affiliate":     {"impressions_mean": 25_000, "ctr": 0.035, "cvr": 0.028, "cpc": 0.80, "aov": 78},
    "SEO_Organic":   {"impressions_mean": 55_000, "ctr": 0.062, "cvr": 0.045, "cpc": 0.00, "aov": 88},
    "Video":         {"impressions_mean": 120_000, "ctr": 0.012, "cvr": 0.014, "cpc": 0.60, "aov": 74},
}

DAYS = 90
START_DATE = pd.Timestamp("2024-10-01")

rows = []
for day in range(DAYS):
    date = START_DATE + pd.Timedelta(days=day)
    # weekend effect — lower traffic on weekends
    day_of_week = date.dayofweek
    weekend_multiplier = 0.78 if day_of_week >= 5 else 1.0
    # slow trend upward (+10% over 90 days)
    trend = 1 + (day / DAYS) * 0.10

    for channel, params in CHANNELS.items():
        imp_base = params["impressions_mean"] * weekend_multiplier * trend
        impressions = int(np.random.normal(imp_base, imp_base * 0.12))
        impressions = max(impressions, 100)

        ctr_noise = np.random.normal(1.0, 0.08)
        clicks = int(impressions * params["ctr"] * ctr_noise)
        clicks = max(clicks, 1)

        cvr_noise = np.random.normal(1.0, 0.12)
        conversions = int(clicks * params["cvr"] * cvr_noise)
        conversions = max(conversions, 0)

        cost = clicks * params["cpc"] * np.random.normal(1.0, 0.05)
        cost = max(cost, 0)

        aov_noise = np.random.normal(1.0, 0.10)
        revenue = conversions * params["aov"] * aov_noise if conversions > 0 else 0

        rows.append({
            "date": date.strftime("%Y-%m-%d"),
            "channel": channel,
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "cost": round(cost, 2),
            "revenue": round(revenue, 2),
        })

df = pd.DataFrame(rows)

# Computed metrics (row-level)
df["ctr"] = df["clicks"] / df["impressions"]
df["conversion_rate"] = df["conversions"] / df["clicks"]
df["cpa"] = df.apply(lambda r: r["cost"] / r["conversions"] if r["conversions"] > 0 else np.nan, axis=1)
df["roas"] = df.apply(lambda r: r["revenue"] / r["cost"] if r["cost"] > 0 else np.nan, axis=1)

out = "C:/Users/eugnm/OneDrive/Desktop/ironhack/Week 6/LAB 9/lab_statistical_analysis_eugen_mueller/data/marketing_data.csv"
df.to_csv(out, index=False)
print(f"Saved {len(df):,} rows to {out}")
print(df.groupby("channel")[["impressions","clicks","conversions","cost","revenue"]].sum().round(0))
