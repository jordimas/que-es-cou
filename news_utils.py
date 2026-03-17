"""Shared utilities for render.py and telegram.py."""

import json
import sys
from pathlib import Path

MONTHS_CA = {
    "01": "gener",    "02": "febrer",   "03": "març",     "04": "abril",
    "05": "maig",     "06": "juny",     "07": "juliol",   "08": "agost",
    "09": "setembre", "10": "octubre",  "11": "novembre", "12": "desembre",
}

SECTION_LABELS = {
    "world":     "Al món",
    "catalunya": "Països Catalans",
    "podcasts":  "Podcasts",
    "events":    "Trobades",
    "videos":    "Vídeos",
}


def format_date_ca(iso: str) -> str:
    """'2026-03-14' or '2026-03-14T19:36' → '14 de març de 2026'"""
    try:
        date_part = iso.split("T")[0]
        y, m, d = date_part.split("-")
        return f"{int(d)} de {MONTHS_CA[m]} de {y}"
    except Exception:
        return iso


def resolve_links(data: dict, links: dict, warn_missing: bool = False) -> list:
    """Resolve link_id → url for all articles. Returns enriched sections list."""
    sections = []
    for sec in data.get("sections", []):
        articles = []
        for art in sec.get("articles", []):
            link_id = art.get("link_id", "")
            url = links.get(link_id, "")
            if not url:
                if warn_missing:
                    print(f"WARNING: link_id '{link_id}' not found in links.json, "
                          f"skipping article: {art.get('title', '')}")
                continue
            articles.append({**art, "url": url})
        if articles:
            sections.append({**sec, "articles": articles})
    return sections


def load_news(base: Path, warn_missing_links: bool = False) -> tuple:
    """Load news.json + links.json, return (data, sections_with_urls)."""
    news_path = base / "news.json"
    links_path = base / "links.json"

    try:
        data = json.loads(news_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"Error: '{news_path}' not found.")
    except json.JSONDecodeError as e:
        sys.exit(f"Error: invalid JSON in '{news_path}': {e}")

    try:
        links = json.loads(links_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        links = {}

    sections = resolve_links(data, links, warn_missing=warn_missing_links)
    return data, sections
