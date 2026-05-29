"""
Part 4 — Statistical Power Analysis
====================================
TLDR (plain English):
    Power = the probability we'd actually *catch* a real difference if it exists.
    If power = 80%, it means: if Channel A really is 15% cheaper than Channel B,
    we'd detect that 8 times out of 10 with our current sample size.
    If power is low, we might be missing real differences — or worse, acting on
    differences that are just noise.

We simulate this empirically: generate fake data thousands of times with a known
planted difference, run the t-test each time, count how often we catch it.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

np.random.seed(42)

OUTPUT_DIR = "outputs/"
DATA_PATH  = "data/marketing_data.csv"
os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH)
df['daily_cpa'] = df.apply(
    lambda r: r['cost'] / r['conversions'] if r['conversions'] > 0 else np.nan, axis=1
)

# Baseline CPA from Paid Search (our anchor channel)
base_cpa = df[df['channel'] == 'Paid_Search']['daily_cpa'].dropna().mean()
print(f"Baseline CPA (Paid Search): ${base_cpa:.2f}")

# =============================================================================
# EMPIRICAL POWER SIMULATION
# =============================================================================

def empirical_power_cpa(true_diff_pct, base_cpa, n_days, n_sim=1000, alpha=0.05):
    """
    Simulate n_sim experiments. Each experiment:
      - generates n_days of CPA data for channel A (baseline)
      - generates n_days of CPA data for channel B (shifted by true_diff_pct)
      - runs Welch t-test
    Returns the fraction of runs where we correctly reject H0 (= power).
    """
    std = base_cpa * 0.15  # realistic day-to-day variation ≈ 15%
    rejections = 0
    mean_b = base_cpa * (1 + true_diff_pct)

    for _ in range(n_sim):
        data_a = np.random.normal(base_cpa, std, n_days)
        data_a = np.maximum(data_a, base_cpa * 0.50)  # cap at 50% of base (no negative CPA)
        data_b = np.random.normal(mean_b,  std, n_days)
        data_b = np.maximum(data_b, mean_b * 0.50)

        from scipy.stats import ttest_ind
        _, p = ttest_ind(data_a, data_b, equal_var=False)
        if p < alpha:
            rejections += 1

    return rejections / n_sim


EFFECT_SIZES  = [0.05, 0.10, 0.15, 0.20]   # 5%, 10%, 15%, 20% CPA difference
SAMPLE_SIZES  = [30, 60, 90, 120, 180]      # days of data

print("\nRunning power simulations (this takes ~30 seconds)...\n")
power_records = []
for eff in EFFECT_SIZES:
    for n in SAMPLE_SIZES:
        pw = empirical_power_cpa(eff, base_cpa, n, n_sim=1000)
        power_records.append({'effect_size_pct': int(eff * 100), 'n_days': n, 'power': pw})
        print(f"  Effect {int(eff*100):>3}%  |  n={n:>3} days  |  Power = {pw:.2f}")

power_df = pd.DataFrame(power_records)

# =============================================================================
# POWER CURVES PLOT
# =============================================================================
fig, ax = plt.subplots(figsize=(10, 6))

colors = ['#e74c3c', '#e67e22', '#2ecc71', '#3498db']
for (eff, group), color in zip(power_df.groupby('effect_size_pct'), colors):
    ax.plot(group['n_days'], group['power'], marker='o', label=f'{eff}% CPA diff',
            color=color, linewidth=2.2, markersize=7)

ax.axhline(0.80, color='black', linewidth=1.5, linestyle='--', label='80% power target')
ax.set_xlabel('Days of Data (Sample Size)')
ax.set_ylabel('Statistical Power')
ax.set_title('Power Analysis — Detecting CPA Differences\n(Paid Search baseline, 15% daily CV)', fontweight='bold')
ax.set_ylim(0, 1.05)
ax.set_xticks(SAMPLE_SIZES)
ax.legend(title='True Effect Size')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR + 'power_analysis_cpa.png', bbox_inches='tight', dpi=120)
plt.show()
print("\nSaved: power_analysis_cpa.png")

# =============================================================================
# PIVOT TABLE — POWER BY EFFECT SIZE × SAMPLE SIZE
# =============================================================================
pivot = power_df.pivot(index='effect_size_pct', columns='n_days', values='power')
pivot.index.name = 'Effect Size (%)'
pivot.columns.name = 'Days'
print("\n=== Power Table (rows = % CPA difference, cols = n days) ===")
print(pivot.map(lambda x: f"{x:.2f}"))

# =============================================================================
# MINIMUM SAMPLE SIZE FOR 80% POWER
# =============================================================================
print("\n=== Minimum Days for 80% Power ===")
current_data_days = 90
print(f"{'Effect Size':>12} | {'Min Days Needed':>16} | {'Current (90d) Status':>22}")
print("-" * 56)
for eff, group in power_df.groupby('effect_size_pct'):
    above80 = group[group['power'] >= 0.80]
    if len(above80):
        min_days = above80['n_days'].min()
        status = "sufficient" if current_data_days >= min_days else f"need {min_days - current_data_days} more days"
    else:
        min_days = ">180"
        status = "insufficient"
    print(f"{eff:>10}%  | {str(min_days):>16} | {status:>22}")

# =============================================================================
# ASSESS POWER FOR OBSERVED SIGNIFICANT PAIRS (from statistical_analysis output)
# =============================================================================
print("\n=== Power Assessment for Statistically Significant CPA Pairs ===")
try:
    cpa_results = pd.read_csv(OUTPUT_DIR + 'cpa_comparisons.csv')
    fdr_sig = cpa_results[cpa_results['significant_fdr'] == True].copy()

    if len(fdr_sig) == 0:
        print("No FDR-significant CPA pairs found — power analysis moot for zero survivors.")
    else:
        for _, row in fdr_sig.iterrows():
            obs_diff_pct = abs(row['pct_difference']) / 100
            pw = empirical_power_cpa(obs_diff_pct, min(row['mean_cpa_a'], row['mean_cpa_b']),
                                      n_days=current_data_days, n_sim=500)
            needed = None
            for n in [30, 60, 90, 120, 180, 270, 365]:
                p_n = empirical_power_cpa(obs_diff_pct, min(row['mean_cpa_a'], row['mean_cpa_b']),
                                           n_days=n, n_sim=300)
                if p_n >= 0.80:
                    needed = n
                    break

            print(f"  {row['channel_a']} vs {row['channel_b']}: "
                  f"obs diff = {row['pct_difference']:.1f}%, "
                  f"power@90d = {pw:.2f}, "
                  f"min days for 80% = {needed if needed else '>365'}")
except FileNotFoundError:
    print("Run statistical_analysis.ipynb first to generate cpa_comparisons.csv")

print("\nPower analysis complete.")
