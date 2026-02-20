"""
13F Fund Tracker — Flask Web Application
"""

import json

import numpy as np
from flask import Flask, render_template, jsonify, request
from flask.json.provider import DefaultJSONProvider

from data.fund_holdings import (
    FUNDS,
    get_all_holdings,
    get_quarter_holdings,
    compute_changes,
    get_cross_fund_holdings,
)


class NumpyJSONProvider(DefaultJSONProvider):
    """Handle numpy types in JSON serialization."""
    def default(self, o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super().default(o)


app = Flask(__name__)
app.json_provider_class = NumpyJSONProvider
app.json = NumpyJSONProvider(app)


# ─── Helpers ──────────────────────────────────────────────────

def _fmt_value(v):
    """Format USD value for JSON serialization."""
    if v >= 1e9:
        return f"${v / 1e9:.1f}B"
    return f"${v / 1e6:.0f}M"


# ─── Pages ────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", funds=FUNDS)


# ─── API Endpoints ────────────────────────────────────────────

@app.route("/api/overview")
def api_overview():
    df = get_all_holdings()
    quarters = sorted(df["quarter"].unique(), reverse=True)
    latest_q = quarters[0]
    df_latest = df[df["quarter"] == latest_q]

    funds_summary = []
    for fund_name, info in FUNDS.items():
        fd = df_latest[df_latest["fund"] == fund_name]
        total = fd["value_usd"].sum()
        top5 = fd.nlargest(5, "value_usd")
        funds_summary.append({
            "name": fund_name,
            "short_name": info["short_name"],
            "style": info["style"],
            "description": info["description"],
            "total_value": total,
            "total_value_fmt": _fmt_value(total),
            "num_positions": int(fd["ticker"].nunique()),
            "top5_concentration": round(top5["pct_portfolio"].sum(), 1),
            "top_holdings": top5[["ticker", "company", "value_usd", "pct_portfolio"]].to_dict("records"),
        })

    return jsonify({"quarter": latest_q, "funds": funds_summary})


@app.route("/api/fund/<fund_short>")
def api_fund(fund_short):
    fund_name = None
    for name, info in FUNDS.items():
        if info["short_name"].lower() == fund_short.lower():
            fund_name = name
            break
    if not fund_name:
        return jsonify({"error": "Fund not found"}), 404

    df = get_all_holdings()
    quarters = sorted(df["quarter"].unique(), reverse=True)
    latest_q = quarters[0]
    fd = df[(df["fund"] == fund_name) & (df["quarter"] == latest_q)]

    holdings = fd.sort_values("value_usd", ascending=False)[
        ["ticker", "company", "sector", "shares", "value_usd", "pct_portfolio"]
    ].to_dict("records")

    sectors = (
        fd.groupby("sector")
        .agg(total_value=("value_usd", "sum"), pct=("pct_portfolio", "sum"))
        .reset_index()
        .sort_values("pct", ascending=False)
        .to_dict("records")
    )

    total = fd["value_usd"].sum()
    return jsonify({
        "fund": fund_name,
        "short_name": FUNDS[fund_name]["short_name"],
        "style": FUNDS[fund_name]["style"],
        "quarter": latest_q,
        "total_value": total,
        "total_value_fmt": _fmt_value(total),
        "num_positions": int(fd["ticker"].nunique()),
        "top5_concentration": round(fd.nlargest(5, "value_usd")["pct_portfolio"].sum(), 1),
        "holdings": holdings,
        "sectors": sectors,
    })


@app.route("/api/changes/<fund_short>")
def api_changes(fund_short):
    fund_name = None
    for name, info in FUNDS.items():
        if info["short_name"].lower() == fund_short.lower():
            fund_name = name
            break
    if not fund_name:
        return jsonify({"error": "Fund not found"}), 404

    df = get_all_holdings()
    quarters = sorted(df["quarter"].unique(), reverse=True)
    if len(quarters) < 2:
        return jsonify({"error": "Need 2+ quarters"}), 400

    changes = compute_changes(fund_name, quarters[0], quarters[1])
    rows = changes.to_dict("records")
    for r in rows:
        for k in r:
            if isinstance(r[k], float) and (r[k] != r[k]):  # NaN check
                r[k] = 0

    summary = {
        "new": int((changes["action"] == "New Position").sum()),
        "increased": int((changes["action"] == "Increased").sum()),
        "reduced": int((changes["action"] == "Reduced").sum()),
        "sold": int((changes["action"] == "Sold Out").sum()),
        "unchanged": int((changes["action"] == "Unchanged").sum()),
    }

    return jsonify({
        "fund": fund_name,
        "current_q": quarters[0],
        "prior_q": quarters[1],
        "summary": summary,
        "changes": rows,
    })


@app.route("/api/crossfund")
def api_crossfund():
    df = get_all_holdings()
    quarters = sorted(df["quarter"].unique(), reverse=True)
    latest_q = quarters[0]
    df_latest = df[df["quarter"] == latest_q]

    cross = get_cross_fund_holdings(latest_q)
    shared = cross[cross["num_funds"] >= 2].sort_values(
        ["num_funds", "total_value"], ascending=[False, False]
    )

    # Overlap matrix
    fund_names = sorted(df_latest["fund_short"].unique())
    fund_tickers = {
        f: set(df_latest[df_latest["fund_short"] == f]["ticker"])
        for f in fund_names
    }
    overlap = {}
    for f1 in fund_names:
        overlap[f1] = {}
        for f2 in fund_names:
            overlap[f1][f2] = len(fund_tickers[f1] & fund_tickers[f2])

    # Heatmap data
    shared_tickers = cross[cross["num_funds"] >= 2]["ticker"].tolist()
    heatmap = []
    for _, row in df_latest[df_latest["ticker"].isin(shared_tickers)].iterrows():
        heatmap.append({
            "ticker": row["ticker"],
            "company": row["company"],
            "fund": row["fund_short"],
            "pct": round(row["pct_portfolio"], 1),
        })

    return jsonify({
        "quarter": latest_q,
        "shared": shared[["ticker", "company", "sector", "num_funds", "funds", "total_value"]].to_dict("records"),
        "overlap": overlap,
        "fund_names": fund_names,
        "heatmap": heatmap,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
