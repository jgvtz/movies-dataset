"""
News Tracker — RSS Feed Fetcher

Fetches articles from configured RSS feeds using stdlib XML parsing,
and returns normalised article dicts.
"""

import hashlib
import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional

import requests

from news_tracker.config import RSS_FEEDS

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 15


def _make_id(url: str) -> str:
    """Deterministic article ID from its URL."""
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def _clean_html(raw: str) -> str:
    """Strip HTML tags from a string."""
    return re.sub(r"<[^>]+>", "", raw).strip()


def _parse_rfc822(date_str: str) -> datetime:
    """Parse RFC-822 dates commonly found in RSS feeds."""
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        return datetime.now(timezone.utc)


def _parse_iso(date_str: str) -> datetime:
    """Parse ISO-8601 / Atom date strings."""
    try:
        # Handle trailing Z
        date_str = date_str.replace("Z", "+00:00")
        return datetime.fromisoformat(date_str)
    except Exception:
        return datetime.now(timezone.utc)


def _text(element, tag: str, namespaces: dict | None = None) -> str:
    """Safely extract text from a child element."""
    child = element.find(tag, namespaces)
    if child is not None and child.text:
        return child.text.strip()
    return ""


def _parse_rss_items(root: ET.Element) -> list[dict]:
    """Parse RSS 2.0 <item> elements."""
    articles = []
    channel = root.find("channel")
    if channel is None:
        return articles

    for item in channel.findall("item"):
        link = _text(item, "link")
        if not link:
            continue
        title = _text(item, "title") or "No title"
        desc = _clean_html(_text(item, "description"))[:500]
        pub_date = _text(item, "pubDate")
        published = _parse_rfc822(pub_date) if pub_date else datetime.now(timezone.utc)

        articles.append({
            "id": _make_id(link),
            "title": title,
            "summary": desc,
            "url": link,
            "published": published,
        })
    return articles


def _parse_atom_entries(root: ET.Element) -> list[dict]:
    """Parse Atom <entry> elements."""
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    articles = []

    for entry in root.findall("atom:entry", ns):
        # Atom links are in <link> attributes
        link_el = entry.find("atom:link[@rel='alternate']", ns)
        if link_el is None:
            link_el = entry.find("atom:link", ns)
        link = link_el.get("href", "") if link_el is not None else ""
        if not link:
            continue

        title = _text(entry, "atom:title", ns) or "No title"
        summary_el = entry.find("atom:summary", ns) or entry.find("atom:content", ns)
        summary = _clean_html(summary_el.text or "")[:500] if summary_el is not None and summary_el.text else ""
        updated = _text(entry, "atom:updated", ns) or _text(entry, "atom:published", ns)
        published = _parse_iso(updated) if updated else datetime.now(timezone.utc)

        articles.append({
            "id": _make_id(link),
            "title": title,
            "summary": summary,
            "url": link,
            "published": published,
        })
    return articles


def fetch_feed(feed_cfg: dict) -> list[dict]:
    """
    Fetch and parse a single RSS/Atom feed.

    Returns a list of article dicts with keys:
        id, title, summary, url, source, category, published
    """
    url = feed_cfg["url"]
    name = feed_cfg["name"]
    category = feed_cfg.get("category", "general")

    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers={
            "User-Agent": "NewsTracker/1.0"
        })
        resp.raise_for_status()
    except Exception as exc:
        logger.warning("Failed to fetch feed %s (%s): %s", name, url, exc)
        return []

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as exc:
        logger.warning("Failed to parse XML from %s: %s", name, exc)
        return []

    # Detect format: RSS 2.0 vs Atom
    if root.tag == "rss" or root.find("channel") is not None:
        articles = _parse_rss_items(root)
    elif root.tag.endswith("feed") or root.find("{http://www.w3.org/2005/Atom}entry") is not None:
        articles = _parse_atom_entries(root)
    else:
        # Try RSS as fallback
        articles = _parse_rss_items(root)

    # Enrich with source metadata
    for art in articles:
        art["source"] = name
        art["category"] = category

    logger.info("Fetched %d articles from %s", len(articles), name)
    return articles


def fetch_all_feeds(feeds: Optional[list[dict]] = None) -> list[dict]:
    """Fetch articles from all configured feeds."""
    feeds = feeds or RSS_FEEDS
    all_articles = []
    for feed_cfg in feeds:
        all_articles.extend(fetch_feed(feed_cfg))
    logger.info("Total articles fetched: %d", len(all_articles))
    return all_articles
