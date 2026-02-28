"""
13F Fund Tracker — Flask Web Application
"""

import json
import logging

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
from news_tracker.config import TOPICS, MIN_RELEVANCE_SCORE, RSS_FEEDS
from news_tracker.fetcher import fetch_all_feeds
from news_tracker.analyzer import classify_article
from news_tracker.storage import (
    init_db,
    upsert_articles,
    query_articles,
    get_sources,
    get_stats,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

# Initialise news tracker DB
init_db()


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


# ─── News Tracker API ────────────────────────────────────────

@app.route("/api/news")
def api_news():
    """Query stored news articles with optional filters."""
    topic_id = request.args.get("topic")
    source = request.args.get("source")
    min_score = int(request.args.get("min_score", MIN_RELEVANCE_SCORE))
    search = request.args.get("search") or None
    limit = int(request.args.get("limit", 200))

    articles = query_articles(
        topic_id=topic_id if topic_id else None,
        source=source if source else None,
        min_score=min_score,
        search=search,
        limit=limit,
    )
    return jsonify({"articles": articles, "count": len(articles)})


@app.route("/api/news/fetch", methods=["POST"])
def api_news_fetch():
    """Fetch latest articles from RSS feeds, analyze, and store."""
    raw_articles = fetch_all_feeds()
    relevant = []
    for art in raw_articles:
        topics = classify_article(art)
        if topics:
            relevant.append((art, topics))
    upsert_articles(relevant)
    return jsonify({
        "fetched": len(raw_articles),
        "relevant": len(relevant),
        "feeds": len(RSS_FEEDS),
    })


@app.route("/api/news/stats")
def api_news_stats():
    """Return news article stats."""
    return jsonify(get_stats())


@app.route("/api/news/sources")
def api_news_sources():
    """Return distinct article sources."""
    return jsonify({"sources": get_sources()})


@app.route("/api/news/topics")
def api_news_topics():
    """Return configured topics."""
    topics_list = []
    for tid, tcfg in TOPICS.items():
        topics_list.append({
            "id": tid,
            "label": tcfg["label"],
            "description": tcfg["description"],
            "keyword_count": len(tcfg["keywords"]),
        })
    return jsonify({"topics": topics_list})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
