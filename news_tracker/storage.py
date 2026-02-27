"""
News Tracker — SQLite Storage Layer

Persists articles and their topic scores so we can show history,
avoid re-fetching, and provide fast filtering.
"""

import json
import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "news_tracker.db"


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS articles (
            id          TEXT PRIMARY KEY,
            title       TEXT NOT NULL,
            summary     TEXT,
            url         TEXT NOT NULL,
            source      TEXT,
            category    TEXT,
            published   TEXT,
            fetched_at  TEXT
        );

        CREATE TABLE IF NOT EXISTS article_topics (
            article_id  TEXT NOT NULL,
            topic_id    TEXT NOT NULL,
            label       TEXT,
            score       INTEGER,
            PRIMARY KEY (article_id, topic_id),
            FOREIGN KEY (article_id) REFERENCES articles(id)
        );

        CREATE INDEX IF NOT EXISTS idx_articles_published
            ON articles(published DESC);
        CREATE INDEX IF NOT EXISTS idx_article_topics_topic
            ON article_topics(topic_id);
        CREATE INDEX IF NOT EXISTS idx_article_topics_score
            ON article_topics(score DESC);
    """)
    conn.commit()
    conn.close()
    logger.info("Database initialised at %s", DB_PATH)


def upsert_article(article: dict, topics: list[dict]):
    """Insert or update an article and its topic scores."""
    conn = _get_conn()
    now = datetime.now(timezone.utc).isoformat()
    pub = article["published"]
    if isinstance(pub, datetime):
        pub = pub.isoformat()

    conn.execute(
        """INSERT INTO articles (id, title, summary, url, source, category, published, fetched_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(id) DO UPDATE SET
               title=excluded.title,
               summary=excluded.summary,
               fetched_at=excluded.fetched_at""",
        (article["id"], article["title"], article["summary"],
         article["url"], article["source"], article["category"],
         pub, now),
    )

    for t in topics:
        conn.execute(
            """INSERT INTO article_topics (article_id, topic_id, label, score)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(article_id, topic_id) DO UPDATE SET
                   score=excluded.score,
                   label=excluded.label""",
            (article["id"], t["topic_id"], t["label"], t["score"]),
        )

    conn.commit()
    conn.close()


def upsert_articles(articles_with_topics: list[tuple[dict, list[dict]]]):
    """Batch upsert multiple (article, topics) pairs."""
    for article, topics in articles_with_topics:
        upsert_article(article, topics)


def query_articles(
    topic_id: str | None = None,
    source: str | None = None,
    min_score: int = 0,
    limit: int = 100,
    offset: int = 0,
    search: str | None = None,
) -> list[dict]:
    """
    Query stored articles with optional filters.

    Returns a list of dicts with article fields plus a 'topics' list.
    """
    conn = _get_conn()

    where_clauses = []
    params = []

    if topic_id:
        where_clauses.append("at.topic_id = ?")
        params.append(topic_id)
    if source:
        where_clauses.append("a.source = ?")
        params.append(source)
    if min_score > 0:
        where_clauses.append("at.score >= ?")
        params.append(min_score)
    if search:
        where_clauses.append("(a.title LIKE ? OR a.summary LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])

    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    sql = f"""
        SELECT DISTINCT a.id, a.title, a.summary, a.url, a.source,
               a.category, a.published, a.fetched_at
        FROM articles a
        JOIN article_topics at ON a.id = at.article_id
        {where_sql}
        ORDER BY a.published DESC
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])

    rows = conn.execute(sql, params).fetchall()

    results = []
    for row in rows:
        article = dict(row)
        # Attach topics
        topics = conn.execute(
            "SELECT topic_id, label, score FROM article_topics WHERE article_id = ? ORDER BY score DESC",
            (article["id"],),
        ).fetchall()
        article["topics"] = [dict(t) for t in topics]
        results.append(article)

    conn.close()
    return results


def get_sources() -> list[str]:
    """Return distinct source names in the DB."""
    conn = _get_conn()
    rows = conn.execute("SELECT DISTINCT source FROM articles ORDER BY source").fetchall()
    conn.close()
    return [r["source"] for r in rows]


def get_stats() -> dict:
    """Return basic DB stats."""
    conn = _get_conn()
    total = conn.execute("SELECT COUNT(*) AS c FROM articles").fetchone()["c"]
    by_topic = conn.execute(
        "SELECT topic_id, label, COUNT(*) AS c FROM article_topics GROUP BY topic_id ORDER BY c DESC"
    ).fetchall()
    conn.close()
    return {
        "total_articles": total,
        "by_topic": [dict(r) for r in by_topic],
    }
