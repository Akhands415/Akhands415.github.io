"""Generate a synthetic marketing campaign dataset (seeded, reproducible).

This is made-up data for a portfolio analysis. It is not from any real company.
Each row is one campaign: spend, impressions, clicks, conversions and revenue.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
# cost per click, click-through rate, conversion rate, average order value
CHANNELS = {
    "Google Search": dict(cpc=1.20, ctr=0.060, cvr=0.045, aov=85,  spend=9000),
    "Facebook Ads":  dict(cpc=0.70, ctr=0.018, cvr=0.020, aov=70,  spend=7000),
    "Instagram":     dict(cpc=0.90, ctr=0.015, cvr=0.015, aov=65,  spend=6000),
    "LinkedIn":      dict(cpc=4.50, ctr=0.008, cvr=0.030, aov=220, spend=8000),
    "Email":         dict(cpc=0.60, ctr=0.030, cvr=0.050, aov=90,  spend=3000),
}
SEASON = {1: .9, 2: .9, 3: 1.0, 4: 1.0, 5: 1.05, 6: 1.0, 7: .95, 8: .95, 9: 1.05, 10: 1.1, 11: 1.35, 12: 1.25}

rows, cid = [], 1
for month in range(1, 13):
    for ch, p in CHANNELS.items():
        for _ in range(8):
            spend = float(rng.lognormal(np.log(p["spend"] / 8), 0.6))
            clicks = max(1, int(spend / p["cpc"] * rng.normal(1, 0.10)))
            impressions = int(clicks / p["ctr"] * rng.normal(1, 0.10))
            # conversion rate falls a little as a campaign gets bigger (diminishing returns)
            cvr = p["cvr"] * (spend / (p["spend"] / 8)) ** -0.12 * SEASON[month] * rng.normal(1, 0.10)
            conversions = int(rng.binomial(clicks, min(max(cvr, 0), 1)))
            revenue = conversions * p["aov"] * rng.lognormal(0, 0.12)
            rows.append((f"C{cid:04d}", f"2025-{month:02d}", ch, round(spend, 2), impressions, clicks, conversions, round(revenue, 2)))
            cid += 1

df = pd.DataFrame(rows, columns=["campaign_id", "month", "channel", "spend", "impressions", "clicks", "conversions", "revenue"])
df.to_csv("marketing_campaigns.csv", index=False)
print(f"wrote marketing_campaigns.csv with {len(df)} campaigns")
