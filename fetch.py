#!/usr/bin/env python3
"""
fetch.py - Fetches all RSS/Atom feeds from sources.yaml and writes raw_feeds.json.

Usage:
    python fetch.py                         # sources.yaml -> raw_feeds.json
    python fetch.py sources.yaml out.json   # custom paths
"""

import json
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import httpx
import yaml

# ── CLI args ───────────────────────────────────────────────────────────────────
sources_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("sources.yaml")
output_path  = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("raw_feeds.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0"
    ),
    "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
}
TIMEOUT = 15  # seconds per request
MAX_WORKERS = 20

# ── Namespaces commonly found in RSS/Atom feeds ────────────────────────────────
NS = {
    "dc":      "http://purl.org/dc/elements/1.1/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "atom":    "http://www.w3.org/2005/Atom",
    "media":   "http://search.yahoo.com/mrss/",
}


def text(el, *tags) -> str:
    """Return stripped text of the first matching child tag, or ''."""
    for tag in tags:
        for child in (el.find(tag), el.find(f"dc:{tag}", NS), el.find(f"atom:{tag}", NS)):
            if child is not None and child.text:
                return child.text.strip()
    return ""


def parse_feed(content: bytes) -> list[dict]:
    """Parse RSS or Atom XML bytes into a list of item dicts."""
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return []

    # Strip default namespace if present (common in Atom)
    tag = root.tag
    if tag == "{http://www.w3.org/2005/Atom}feed" or tag == "feed":
        # Atom feed
        items = []
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            link_el = entry.find("{http://www.w3.org/2005/Atom}link[@rel='alternate']")
            if link_el is None:
                link_el = entry.find("{http://www.w3.org/2005/Atom}link")
            link = link_el.get("href", "") if link_el is not None else ""
            pub = (
                text(entry, "{http://www.w3.org/2005/Atom}published")
                or text(entry, "{http://www.w3.org/2005/Atom}updated")
            )
            title = text(entry, "{http://www.w3.org/2005/Atom}title")
            if not title and not link:
                continue
            items.append({
                "title":       title,
                "link":        link,
                "pubDate":     pub,
                "description": text(entry, "{http://www.w3.org/2005/Atom}summary",
                                         "{http://www.w3.org/2005/Atom}content"),
            })
        return items

    # RSS feed — find <channel><item> elements
    items = []
    for item in root.iter("item"):
        link = text(item, "link")
        # Some feeds put the URL in <guid isPermaLink="true">
        if not link:
            guid = item.find("guid")
            if guid is not None and guid.get("isPermaLink", "true").lower() != "false":
                link = (guid.text or "").strip()
        title = text(item, "title")
        if not title and not link:
            continue
        pub = text(item, "pubDate") or item.findtext("dc:date", namespaces=NS) or ""
        desc = text(item, "description") or item.findtext("content:encoded", namespaces=NS) or ""
        items.append({
            "title":       title,
            "link":        link,
            "pubDate":     pub,
            "description": desc,
        })
    return items


def fetch_source(client: httpx.Client, name: str, url: str) -> dict:
    """Fetch a single source URL and return a result dict."""
    result = {"name": name, "url": url}
    try:
        resp = client.get(url)
        if resp.status_code == 200:
            result["status"] = "ok"
            result["items"] = parse_feed(resp.content)
        else:
            result["status"] = "blocked" if resp.status_code in (401, 403) else "error"
            result["error_detail"] = f"HTTP {resp.status_code} {resp.reason_phrase}"
            result["items"] = []
    except httpx.TimeoutException:
        result["status"] = "error"
        result["error_detail"] = "Connection timeout"
        result["items"] = []
    except Exception as e:
        result["status"] = "error"
        result["error_detail"] = str(e)
        result["items"] = []
    return result


def fetch_section(section_id: str, sources: list[dict]) -> dict:
    """Fetch all sources for a section concurrently."""
    with httpx.Client(headers=HEADERS, timeout=TIMEOUT, follow_redirects=True) as client:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(fetch_source, client, s["name"], s["url"]): s
                for s in sources
            }
            results = [f.result() for f in as_completed(futures)]

    # Preserve original source order
    order = {s["name"]: i for i, s in enumerate(sources)}
    results.sort(key=lambda r: order[r["name"]])

    ok = sum(1 for r in results if r["status"] == "ok")
    total_items = sum(len(r["items"]) for r in results)
    print(f"  [{section_id}] {ok}/{len(sources)} sources ok, {total_items} items total")
    return {"id": section_id, "sources": results}


# ── Main ───────────────────────────────────────────────────────────────────────
try:
    sources_data = yaml.safe_load(sources_path.read_text(encoding="utf-8"))
except FileNotFoundError:
    sys.exit(f"Error: '{sources_path}' not found.")

SECTION_IDS = ["world", "catalunya", "podcasts", "events"]

fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M")
print(f"Fetching feeds at {fetched_at} ...")

sections = []
for section_id in SECTION_IDS:
    section_sources = sources_data.get(section_id, [])
    if not section_sources:
        print(f"  [{section_id}] no sources defined, skipping")
        continue
    sections.append(fetch_section(section_id, section_sources))

output = {"fetched_at": fetched_at, "sections": sections}
output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Written to '{output_path}'")
