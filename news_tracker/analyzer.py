"""
News Tracker — Keyword Analyzer & Relevance Scoring

Scores each article against configured topics based on keyword matches
in titles and summaries.  Title matches are weighted more heavily.
"""

import re
from news_tracker.config import TOPICS, MIN_RELEVANCE_SCORE

# Weights
TITLE_WEIGHT = 3
SUMMARY_WEIGHT = 1
# Bonus per keyword match (capped)
MATCH_BONUS = 10
MAX_SCORE = 100


def _count_keyword_hits(text: str, keywords: list[str]) -> int:
    """Count how many distinct keywords appear in *text* (case-insensitive)."""
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw.lower() in text_lower)


def score_article(article: dict, topic_id: str) -> int:
    """
    Return a relevance score (0-100) for *article* against the given topic.

    Scoring:
      - Each keyword found in the title  → MATCH_BONUS * TITLE_WEIGHT
      - Each keyword found in the summary → MATCH_BONUS * SUMMARY_WEIGHT
    The total is capped at MAX_SCORE.
    """
    topic = TOPICS.get(topic_id)
    if not topic:
        return 0

    keywords = topic["keywords"]
    title_hits = _count_keyword_hits(article.get("title", ""), keywords)
    summary_hits = _count_keyword_hits(article.get("summary", ""), keywords)

    raw = (title_hits * MATCH_BONUS * TITLE_WEIGHT
           + summary_hits * MATCH_BONUS * SUMMARY_WEIGHT)
    return min(raw, MAX_SCORE)


def classify_article(article: dict) -> list[dict]:
    """
    Score an article against every topic.

    Returns a list of dicts: [{"topic_id": ..., "label": ..., "score": ...}, ...]
    Only topics whose score >= MIN_RELEVANCE_SCORE are included, sorted
    descending by score.
    """
    results = []
    for topic_id, topic_cfg in TOPICS.items():
        sc = score_article(article, topic_id)
        if sc >= MIN_RELEVANCE_SCORE:
            results.append({
                "topic_id": topic_id,
                "label": topic_cfg["label"],
                "score": sc,
            })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def highlight_keywords(text: str, topic_id: str) -> str:
    """
    Wrap matching keywords in **bold** markdown for display.
    """
    topic = TOPICS.get(topic_id)
    if not topic:
        return text
    for kw in sorted(topic["keywords"], key=len, reverse=True):
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        text = pattern.sub(lambda m: f"**{m.group()}**", text)
    return text
