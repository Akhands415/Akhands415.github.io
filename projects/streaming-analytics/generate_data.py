"""Generate a synthetic daily streaming dataset with realistic problems baked in.

All data is made up (seeded, reproducible). It is NOT real platform or employer data.
Planted issues the pipeline should catch:
  * duplicate rows, null track ids, negative stream counts
  * a 5-day gap in NetEase data (like a delayed source table)
  * one track going viral on a single platform (an anomaly)
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
DAYS = pd.date_range("2025-01-01", periods=180, freq="D")
PLATFORMS = {"Spotify": 1.00, "Amazon Music": 0.45, "NetEase": 0.30, "Tencent": 0.22}
N_TRACKS = 40

tracks = pd.DataFrame({
    "track_id": [f"T{i:03d}" for i in range(1, N_TRACKS + 1)],
    "base": rng.lognormal(mean=9.0, sigma=0.8, size=N_TRACKS),
})

rows = []
for p, w in PLATFORMS.items():
    for _, t in tracks.iterrows():
        trend = np.linspace(1.0, 1.0 + rng.uniform(-0.2, 0.6), len(DAYS))
        weekend = np.where(DAYS.dayofweek >= 5, 1.15, 1.0)
        noise = rng.normal(1.0, 0.08, len(DAYS))
        s = t["base"] * w * trend * weekend * noise / 30
        rows.append(pd.DataFrame({"stream_date": DAYS, "platform": p,
                                  "track_id": t["track_id"], "streams": s.round().astype(int)}))
df = pd.concat(rows, ignore_index=True)

# planted issues
viral = (df.track_id == "T007") & (df.platform == "Spotify") & (df.stream_date >= "2025-04-10") & (df.stream_date <= "2025-04-16")
df.loc[viral, "streams"] = (df.loc[viral, "streams"] * 6).astype(int)

gap = (df.platform == "NetEase") & (df.stream_date >= "2025-05-10") & (df.stream_date <= "2025-05-14")
df = df[~gap]

dups = df.sample(40, random_state=1)
df = pd.concat([df, dups], ignore_index=True)
df.loc[df.sample(15, random_state=2).index, "track_id"] = None
df.loc[df.sample(10, random_state=3).index, "streams"] = -1

df["stream_date"] = df["stream_date"].dt.strftime("%Y-%m-%d")
df.sample(frac=1, random_state=4).to_csv("data/raw_streams.csv", index=False)
print(f"wrote data/raw_streams.csv with {len(df):,} rows")
