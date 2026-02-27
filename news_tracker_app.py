"""
News Tracker — Streamlit Application

Track financial news on alternative managers, private credit,
private equity, real assets, and custom topics.

Run with:
    streamlit run news_tracker_app.py
"""

import logging
from datetime import datetime, timezone

import streamlit as st

from news_tracker.config import TOPICS, MIN_RELEVANCE_SCORE, RSS_FEEDS
from news_tracker.fetcher import fetch_all_feeds
from news_tracker.analyzer import classify_article, highlight_keywords
from news_tracker.storage import (
    init_db,
    upsert_articles,
    query_articles,
    get_sources,
    get_stats,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="News Tracker — Alt Managers & Private Credit",
    page_icon="📰",
    layout="wide",
)

# Initialise DB on first run
init_db()

# ─── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    .article-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        background: #fafafa;
    }
    .article-card:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .score-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .score-high   { background: #c8e6c9; color: #2e7d32; }
    .score-medium { background: #fff9c4; color: #f57f17; }
    .score-low    { background: #e0e0e0; color: #616161; }
    .topic-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 8px;
        font-size: 0.75rem;
        margin-right: 4px;
        background: #e3f2fd;
        color: #1565c0;
    }
    .source-tag {
        font-size: 0.75rem;
        color: #888;
    }
    .stat-box {
        text-align: center;
        padding: 1rem;
        border-radius: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .stat-box h2 { margin: 0; font-size: 2rem; }
    .stat-box p  { margin: 0; font-size: 0.85rem; opacity: 0.85; }
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.title("News Tracker")
    st.caption("Alternative Managers & Private Credit")
    st.divider()

    # Topic filter
    st.subheader("Filter by Topic")
    selected_topic = st.selectbox(
        "Topic",
        options=["All Topics"] + list(TOPICS.keys()),
        format_func=lambda x: "All Topics" if x == "All Topics" else TOPICS[x]["label"],
    )
    topic_filter = None if selected_topic == "All Topics" else selected_topic

    # Score filter
    min_score = st.slider(
        "Minimum Relevance Score",
        min_value=0,
        max_value=100,
        value=MIN_RELEVANCE_SCORE,
        step=5,
    )

    # Source filter
    db_sources = get_sources()
    source_filter = st.selectbox(
        "Source",
        options=["All Sources"] + db_sources,
    )
    source_filter = None if source_filter == "All Sources" else source_filter

    # Search
    search_query = st.text_input("Search articles", placeholder="e.g. Blackstone, CLO, direct lending")

    st.divider()

    # Fetch button
    if st.button("Fetch Latest News", type="primary", use_container_width=True):
        with st.spinner("Fetching RSS feeds..."):
            raw_articles = fetch_all_feeds()
            st.info(f"Fetched {len(raw_articles)} articles from {len(RSS_FEEDS)} feeds")

        with st.spinner("Analyzing relevance..."):
            relevant = []
            for art in raw_articles:
                topics = classify_article(art)
                if topics:
                    relevant.append((art, topics))

            upsert_articles(relevant)
            st.success(f"Stored {len(relevant)} relevant articles")

        st.rerun()

    st.divider()
    st.subheader("Tracked Topics")
    for tid, tcfg in TOPICS.items():
        st.markdown(f"**{tcfg['label']}**")
        st.caption(tcfg["description"])
        st.caption(f"{len(tcfg['keywords'])} keywords tracked")


# ─── Main Content ─────────────────────────────────────────────

st.title("News Tracker")
st.markdown("Track news across **alternative managers**, **private credit**, **private equity**, and **real assets**.")

# Stats row
stats = get_stats()
cols = st.columns(len(stats["by_topic"]) + 1)
with cols[0]:
    st.metric("Total Articles", stats["total_articles"])
for i, t in enumerate(stats["by_topic"]):
    with cols[i + 1]:
        st.metric(t["label"], t["c"])

st.divider()

# ─── Article Feed ─────────────────────────────────────────────
articles = query_articles(
    topic_id=topic_filter,
    source=source_filter,
    min_score=min_score,
    search=search_query if search_query else None,
    limit=200,
)

if not articles:
    st.info(
        "No articles yet. Click **Fetch Latest News** in the sidebar to pull "
        "articles from RSS feeds and score them against your topics."
    )
else:
    st.subheader(f"Articles ({len(articles)})")

    for art in articles:
        with st.container():
            # Header row
            col1, col2 = st.columns([5, 1])
            with col1:
                # Title with link
                st.markdown(f"### [{art['title']}]({art['url']})")
            with col2:
                top_score = max((t["score"] for t in art["topics"]), default=0)
                if top_score >= 60:
                    badge_class = "score-high"
                elif top_score >= 30:
                    badge_class = "score-medium"
                else:
                    badge_class = "score-low"
                st.markdown(
                    f'<span class="score-badge {badge_class}">Score: {top_score}</span>',
                    unsafe_allow_html=True,
                )

            # Topic tags
            tags_html = ""
            for t in art["topics"]:
                tags_html += f'<span class="topic-tag">{t["label"]} ({t["score"]})</span>'
            tags_html += f' <span class="source-tag">{art["source"]}</span>'
            if art.get("published"):
                pub_str = art["published"]
                if isinstance(pub_str, str) and len(pub_str) >= 10:
                    tags_html += f' <span class="source-tag"> | {pub_str[:10]}</span>'
            st.markdown(tags_html, unsafe_allow_html=True)

            # Summary with highlights
            summary = art.get("summary", "")
            if summary and topic_filter:
                summary = highlight_keywords(summary, topic_filter)
            if summary:
                st.markdown(summary[:300] + ("..." if len(summary) > 300 else ""))

            st.divider()


# ─── Footer ───────────────────────────────────────────────────
st.caption("News Tracker v1.0 — Powered by RSS feeds and keyword analysis")
