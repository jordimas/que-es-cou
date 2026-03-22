#!/usr/bin/env python3
"""
fetch.py - Fetches all RSS/Atom feeds from sources.yaml and writes one JSON per category.

Usage:
    python fetch.py                      # sources.yaml -> raw_feeds_<category>.json
    python fetch.py sources.yaml outdir/ # custom sources and output directory
"""

import hashlib
import json
import sys
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path

import httpx
import yaml

# ── CLI args ───────────────────────────────────────────────────────────────────
sources_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("config/sources.yaml")
output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("output")

feed_age_path = sources_path.parent / "feed_age.json"
FEED_AGE = json.loads(feed_age_path.read_text()) if feed_age_path.exists() else {}

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
    "dc": "http://purl.org/dc/elements/1.1/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "atom": "http://www.w3.org/2005/Atom",
    "media": "http://search.yahoo.com/mrss/",
}


def text(el, *tags) -> str:
    """Return stripped text of the first matching child tag, or ''."""
    for tag in tags:
        for child in (
            el.find(tag),
            el.find(f"dc:{tag}", NS),
            el.find(f"atom:{tag}", NS),
        ):
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
            pub = text(entry, "{http://www.w3.org/2005/Atom}published") or text(
                entry, "{http://www.w3.org/2005/Atom}updated"
            )
            title = text(entry, "{http://www.w3.org/2005/Atom}title")
            if not title and not link:
                continue
            items.append(
                {
                    "title": title,
                    "link": link,
                    "pubDate": pub,
                    "description": text(
                        entry,
                        "{http://www.w3.org/2005/Atom}summary",
                        "{http://www.w3.org/2005/Atom}content",
                    ),
                }
            )
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
        desc = (
            text(item, "description")
            or item.findtext("content:encoded", namespaces=NS)
            or ""
        )
        items.append(
            {
                "title": title,
                "link": link,
                "pubDate": pub,
                "description": desc,
            }
        )
    return items


def fetch_source(client: httpx.Client, name: str, url: str, retries: int = 2) -> dict:
    """Fetch a single source URL and return a result dict."""
    result = {"name": name, "url": url}
    for attempt in range(1 + retries):
        try:
            resp = client.get(url)
            if resp.status_code == 200:
                result["status"] = "ok"
                result["items"] = parse_feed(resp.content)
                return result
            elif resp.status_code in (401, 403):
                result["status"] = "blocked"
                result["error_detail"] = f"HTTP {resp.status_code} {resp.reason_phrase}"
                result["items"] = []
                return result
            else:
                result["error_detail"] = f"HTTP {resp.status_code} {resp.reason_phrase}"
        except httpx.TimeoutException:
            result["error_detail"] = "Connection timeout"
        except Exception as e:
            result["error_detail"] = str(e)
        if attempt < retries:
            time.sleep(2**attempt)
    result["status"] = "error"
    result["items"] = []
    return result


def filter_by_age(items: list[dict], max_days: int) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_days)
    result = []
    for item in items:
        try:
            pub = parsedate_to_datetime(item.get("pubDate", ""))
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
            if pub >= cutoff:
                result.append(item)
        except Exception:
            result.append(item)  # keep items with unparseable dates
    return result


def fetch_section(section_id: str, sources: list[dict]) -> dict:
    """Fetch all sources for a section concurrently."""
    with httpx.Client(
        headers=HEADERS, timeout=TIMEOUT, follow_redirects=True
    ) as client:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(fetch_source, client, s["name"], s["url"]): s
                for s in sources
            }
            tech_flags = {s["name"]: s.get("tech", False) for s in sources}
    results = [f.result() for f in as_completed(futures)]
    for r in results:
        if tech_flags.get(r["name"]):
            r["tech"] = True

    # Preserve original source order
    order = {s["name"]: i for i, s in enumerate(sources)}
    results.sort(key=lambda r: order[r["name"]])

    ok = sum(1 for r in results if r["status"] == "ok")
    total_items = sum(len(r.get("items", [])) for r in results)
    print(
        f"  [{section_id}] {ok}/{len(sources)} sources ok, {total_items} items fetched"
    )
    for r in results:
        if r["status"] != "ok":
            print(
                f"    [{r['status']}] {r['name']} ({r['url']}): {r.get('error_detail', '')}"
            )
    return {"id": section_id, "sources": results}


# ── Main ───────────────────────────────────────────────────────────────────────
try:
    sources_data = yaml.safe_load(sources_path.read_text(encoding="utf-8"))
except FileNotFoundError:
    sys.exit(f"Error: '{sources_path}' not found.")

output_dir.mkdir(exist_ok=True)

SECTION_IDS = ["world", "economy", "catalunya", "podcasts", "events", "videos"]

fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M")
print(f"Fetching feeds at {fetched_at} ...")

links = {}
tech_approved = {}  # section_id -> [link_ids] pre-approved from tech: true sources

for section_id in SECTION_IDS:
    section_sources = sources_data.get(section_id, [])
    if not section_sources:
        print(f"  [{section_id}] no sources defined, skipping")
        continue
    section = fetch_section(section_id, section_sources)
    max_days = FEED_AGE.get(section_id, {}).get("days")
    approved = []
    for source in section["sources"]:
        if max_days:
            source["items"] = filter_by_age(source.get("items", []), max_days)
        is_tech = source.get("tech", False)
        for item in source.get("items", []):
            link = item.get("link", "")
            if link:
                link_id = "c_" + hashlib.sha1(link.encode()).hexdigest()[-6:]
                links[link_id] = link
                item["link_id"] = link_id
            if is_tech and item.get("link_id"):
                approved.append(item["link_id"])
        # Remove tech: true items from source so they don't enter the classifier
        if is_tech:
            source["items"] = []
    if approved:
        tech_approved[section_id] = approved
    if max_days:
        kept = sum(len(s.get("items", [])) for s in section["sources"])
        print(
            f"  [{section_id}] {kept} items need classification, {len(approved)} auto-approved"
        )
    out_path = output_dir / f"raw_feeds_{section_id}.json"
    out_path.write_text(
        json.dumps(
            {"fetched_at": fetched_at, "section": section}, ensure_ascii=False, indent=2
        ),
        encoding="utf-8",
    )
    print(f"  Written to '{out_path}'")

links_path = output_dir / "links.json"
links_path.write_text(json.dumps(links, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  Written to '{links_path}'")

approved_path = output_dir / "tech_approved.json"
approved_path.write_text(
    json.dumps(tech_approved, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(f"  Written to '{approved_path}'")
