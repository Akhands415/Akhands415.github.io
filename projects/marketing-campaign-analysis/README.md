# Marketing Campaign Performance Analysis

An exploratory analysis of 480 campaigns across five channels (Google Search, Facebook Ads, Instagram, LinkedIn and Email) for 2025. It looks at which channels earn their budget, where the funnel leaks, how return changes through the year, and what happens when budget moves.

**The data is synthetic.** `generate_data.py` creates it with a fixed seed, so the analysis can be reproduced but describes this dataset, not a real company.

## Questions answered

1. Which channel returns the most revenue per dollar spent?
2. Where does each channel's funnel (impressions, clicks, conversions) leak?
3. How do spend and return change through the year?
4. Does spending more on a campaign keep paying off?
5. If budget moves between channels, what changes?

## Findings

- Email returned about $7.55 per $1 and Google Search $3.31. Instagram returned $1.07. The overall return was $2.56 per $1.
- November had the best return (3.39) and February the worst (2.03).
- Conversion rate falls from 3.60% in the smallest campaigns to 2.88% in the largest, an elasticity of about -0.09.
- Moving 20% of Instagram's budget to Google Search is estimated to add about 3% to total revenue after allowing for diminishing returns.

The notebook states the limits: synthetic data, an assumed email cost, revenue instead of profit, and no experiment behind the scenario.

## Files

| File | What it is |
|---|---|
| `Marketing Campaign Analysis.ipynb` | The analysis, with code, charts and conclusions |
| `marketing_campaigns.csv` | The dataset |
| `generate_data.py` | Recreates the dataset |

## Run it

```bash
pip install pandas numpy matplotlib seaborn jupyter
python generate_data.py
jupyter notebook "Marketing Campaign Analysis.ipynb"
```

## Tools

Python, Pandas, NumPy, Matplotlib, Seaborn
