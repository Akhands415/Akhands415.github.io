"""Build the models in order, run data-quality tests, and draw the charts."""
import sqlite3
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).parent
con = sqlite3.connect(":memory:")
raw = pd.read_csv(ROOT / "data/raw_streams.csv")
raw.to_sql("raw_streams", con, index=False)

# 1. build models (staging first, then marts), each as a table named after its file
for sql in sorted((ROOT / "models/staging").glob("*.sql")) + sorted((ROOT / "models/marts").glob("*.sql")):
    con.execute(f"CREATE TABLE {sql.stem} AS {sql.read_text()}")
    n = con.execute(f"SELECT COUNT(*) FROM {sql.stem}").fetchone()[0]
    print(f"built {sql.stem:<22} {n:>7,} rows")

# 2. data-quality checks on the raw and staged data
def one(q): return con.execute(q).fetchone()[0]
checks = {
    "raw: null track_id": one("SELECT COUNT(*) FROM raw_streams WHERE track_id IS NULL"),
    "raw: negative streams": one("SELECT COUNT(*) FROM raw_streams WHERE streams < 0"),
    "raw: duplicate rows": one("SELECT COUNT(*) - COUNT(DISTINCT stream_date||platform||track_id) FROM raw_streams WHERE track_id IS NOT NULL"),
    "stg: null track_id": one("SELECT COUNT(*) FROM stg_streams WHERE track_id IS NULL"),
    "stg: negative streams": one("SELECT COUNT(*) FROM stg_streams WHERE streams < 0"),
    "stg: duplicate keys": one("SELECT COUNT(*) - COUNT(DISTINCT stream_date||platform||track_id) FROM stg_streams"),
}
gaps = pd.read_sql((ROOT / "tests/date_gaps.sql").read_text(), con)
checks["stg: missing platform-days"] = len(gaps)
print("\ndata quality")
for k, v in checks.items():
    print(f"  {'PASS' if v == 0 else 'FLAG'}  {k:<28} {v}")
if len(gaps):
    print("\nmissing days:\n", gaps.groupby("platform").missing_date.agg(["min", "max", "count"]).to_string())

# 3. results
daily = pd.read_sql("SELECT * FROM mart_daily_platform", con, parse_dates=["stream_date"])
share = pd.read_sql("SELECT * FROM mart_platform_share", con)
top = pd.read_sql("SELECT * FROM mart_track_summary ORDER BY rank LIMIT 10", con)
anom = pd.read_sql("SELECT * FROM mart_anomalies ORDER BY stream_date", con)
print("\nplatform share, all months:\n", (share.groupby("platform").streams.sum() / share.streams.sum() * 100).round(1).to_string())
print("\ntop 5 tracks:\n", top.head(5).to_string(index=False))
print("\nanomalies:", len(anom)); print(anom.to_string(index=False))

# 4. charts
COL = {"Spotify": "#1B8F6B", "Amazon Music": "#2F6BFF", "NetEase": "#F2574A", "Tencent": "#F2A900"}
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
(ROOT / "charts").mkdir(exist_ok=True)

fig, ax = plt.subplots(figsize=(9, 4.2))
for p, g in daily.groupby("platform"):
    ax.plot(g.stream_date, g.streams_7d_avg, label=p, color=COL[p], lw=2)
if len(gaps):
    g0, g1 = pd.to_datetime(gaps.missing_date.min()), pd.to_datetime(gaps.missing_date.max())
    ax.axvspan(g0, g1, color="#F2574A", alpha=0.15)
    ax.annotate("NetEase source gap", (g0, ax.get_ylim()[1] * 0.92), fontsize=9, color="#B3261E")
ax.set_title("Daily streams by platform (7-day average)", loc="left", fontweight="bold")
ax.set_ylabel("Streams"); ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.1))
fig.tight_layout(); fig.savefig(ROOT / "charts/daily_streams.png", dpi=150); plt.close(fig)

piv = share.pivot(index="month", columns="platform", values="share_pct")[list(COL)]
fig, ax = plt.subplots(figsize=(9, 4.2)); bottom = None
for p in piv.columns:
    ax.bar(piv.index, piv[p], bottom=bottom, label=p, color=COL[p])
    bottom = piv[p] if bottom is None else bottom + piv[p]
ax.set_title("Monthly platform share (%)", loc="left", fontweight="bold")
ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.1))
fig.tight_layout(); fig.savefig(ROOT / "charts/platform_share.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 4.2))
ax.barh(top.track_id[::-1], top.streams[::-1] / 1e6, color="#7C4DEB")
ax.set_title("Top 10 tracks by total streams (millions)", loc="left", fontweight="bold")
fig.tight_layout(); fig.savefig(ROOT / "charts/top_tracks.png", dpi=150); plt.close(fig)
print("\ncharts written")
