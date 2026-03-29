#!/usr/bin/env python3
"""
Updated groq_tech_filter.py to use prompts/tech_topic_filter.md.
Merges tech_approved.json (pre-approved from tech: true sources) with classified results.
Writes filtered raw_feeds_*_filtered.json files.
"""

import json
import os
import re
import sys
import time
from pathlib import Path

from groq import Groq, InternalServerError

GROQ_MODEL = os.environ.get("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
CACHE_PATH = Path(__file__).parent / "output" / "filter_cache.json"


def load_task_prompt():
    """Load the tech topic filter prompt from prompts/tech_topic_filter.md."""
    prompt_path = Path(__file__).parent / "prompts" / "tech_topic_filter.md"
    return prompt_path.read_text()


def load_cache() -> dict:
    """Load the filter cache from filter_cache.json."""
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text())
    return {}


def save_cache(cache: dict):
    """Save the filter cache to filter_cache.json."""
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2))


def get_cached_result(link_id: str, cache: dict) -> bool | None:
    """Get cached result for an article ID, or None if not cached."""
    return cache.get(link_id)


def load_articles(path: Path) -> list[dict]:
    """Extract a flat list of {link_id, title, description} from a raw_feeds_*.json file."""
    data = json.loads(path.read_text())
    articles = []
    for source in data.get("section", {}).get("sources", []):
        for item in source.get("items", []):
            desc = re.sub(r"<[^>]+>", " ", item.get("description", ""))
            desc = re.sub(r"\s+", " ", desc).strip()[:200]
            articles.append(
                {
                    "link_id": item.get("link_id", ""),
                    "title": item.get("title", ""),
                    "description": desc,
                }
            )
    return articles


def main():
    base = Path(__file__).parent / "output"
    world_path = Path(os.environ.get("WORLD_PATH", base / "raw_feeds_world.json"))
    catalunya_path = Path(
        os.environ.get("CATALUNYA_PATH", base / "raw_feeds_catalunya.json")
    )
    economy_path = Path(os.environ.get("ECONOMY_PATH", base / "raw_feeds_economy.json"))
    out_path = Path(os.environ.get("OUT_PATH", base / "tech_topic_filter_new.json"))

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("ERROR: GROQ_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    client = Groq(api_key=api_key)
    task_prompt = load_task_prompt()
    cache = load_cache()

    BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 80))
    total_prompt_tokens = 0
    total_completion_tokens = 0
    last_headers: dict = {}
    cache_hits = 0
    cache_misses = 0

    def classify_batch(cat: str, articles: list) -> list:
        nonlocal total_prompt_tokens, total_completion_tokens, last_headers, cache_hits, cache_misses

        # Check cache for each article
        cached_ids = []
        uncached_articles = []
        article_to_id = {}

        for article in articles:
            link_id = article.get("link_id", "")
            cached = get_cached_result(link_id, cache)
            if cached is not None:
                cache_hits += 1
                if cached:  # Only include if True
                    cached_ids.append(link_id)
            else:
                cache_misses += 1
                uncached_articles.append(article)
                article_to_id[article.get("link_id", "")] = article

        # If all cached, return immediately
        if not uncached_articles:
            return cached_ids

        # Only call model for uncached articles
        prompt = task_prompt.format(
            category=cat,
            articles_data=json.dumps(uncached_articles, ensure_ascii=False),
        )
        for attempt in range(5):
            try:
                raw_response = client.with_raw_response.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.0,
                    max_tokens=4096,
                )
                break
            except InternalServerError as e:
                if attempt == 4:
                    raise
                wait = 20 * (2 ** attempt)
                print(f"  [retry] Groq 503, waiting {wait}s (attempt {attempt + 1}/5)...")
                time.sleep(wait)
        response = raw_response.parse()
        if response.usage:
            total_prompt_tokens += response.usage.prompt_tokens
            total_completion_tokens += response.usage.completion_tokens
        last_headers = dict(raw_response.headers)
        raw = response.choices[0].message.content.strip()
        if "<think>" in raw:
            end = raw.rfind("</think>")
            raw = raw[end + len("</think>") :].strip() if end != -1 else raw

        start = raw.find("[")
        end = raw.rfind("]")
        if start != -1 and end > start:
            raw = raw[start : end + 1]

        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                parsed = next(iter(parsed.values()))
        except json.JSONDecodeError:
            repaired = re.sub(r"\b(c_[0-9a-f]+)\b", r'"\1"', raw)
            try:
                parsed = json.loads(repaired)
            except json.JSONDecodeError as e:
                print(
                    f"ERROR: model returned invalid JSON for {cat}: {e}",
                    file=sys.stderr,
                )
                parsed = []

        # Update cache with new results
        for link_id in parsed:
            cache[link_id] = True

        # Cache articles that were not approved (False)
        for article in uncached_articles:
            link_id = article.get("link_id", "")
            if link_id not in cache:
                cache[link_id] = False

        return cached_ids + parsed

    # Load pre-approved tech articles
    approved_path = base / "tech_approved.json"
    tech_approved = {}
    if approved_path.exists():
        tech_approved = json.loads(approved_path.read_text())
        print(
            f"Loaded {sum(len(v) for v in tech_approved.values())} pre-approved tech articles"
        )

    result = {}
    tasks = [
        ("world", world_path),
        ("economy", economy_path),
        ("catalunya", catalunya_path),
    ]

    for cat, path in tasks:
        if not path.exists():
            print(f"Skipping {cat}: {path} not found")
            result[cat] = []
            continue

        articles = load_articles(path)
        print(f"Classifying {len(articles)} {cat} articles...")
        ids: list[str] = []
        for i in range(0, len(articles), BATCH_SIZE):
            batch = articles[i : i + BATCH_SIZE]
            ids.extend(classify_batch(cat, batch))

        # Merge with pre-approved tech articles
        approved_ids = tech_approved.get(cat, [])
        for link_id in approved_ids:
            if link_id not in ids:
                ids.append(link_id)
        result[cat] = ids
        print(
            f"  {cat}: {len(ids)} approved articles ({len(approved_ids)} pre-approved + {len(ids) - len(approved_ids)} classified)"
        )

    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Written to {out_path}")

    # Write filtered raw_feeds_*_filtered.json files
    print("\nWriting filtered feed files...")
    for cat, path in tasks:
        if not path.exists():
            continue

        raw_data = json.loads(path.read_text())
        allowed_ids = set(result.get(cat, []))
        filtered_sources = []
        discarded = []

        for source in raw_data.get("section", {}).get("sources", []):
            filtered_items = []
            for item in source.get("items", []):
                if item.get("link_id") in allowed_ids:
                    filtered_items.append(item)
                else:
                    discarded.append((source["name"], item.get("title", "(no title)")))
            filtered_sources.append({**source, "items": filtered_items})

        filtered_data = {
            **raw_data,
            "section": {**raw_data["section"], "sources": filtered_sources},
        }
        filtered_path = path.parent / f"{path.stem}_filtered.json"
        filtered_path.write_text(
            json.dumps(filtered_data, ensure_ascii=False, indent=2)
        )
        total_items = sum(len(s["items"]) for s in filtered_sources)
        print(f"  {filtered_path.name}: {total_items} articles")

    # Log discarded articles
    log_path = base / "filtered_tech.log"
    log_lines = [f"[{source}] {title}" for source, title in discarded]
    log_path.write_text("\n".join(log_lines) + "\n" if log_lines else "")
    print(f"  Logged {len(log_lines)} discarded articles to {log_path.name}")

    # Save cache
    save_cache(cache)
    print(
        f"\nCache: {cache_hits} hits, {cache_misses} misses ({cache_hits + cache_misses} total checks)"
    )
    print(f"Cache saved to {CACHE_PATH.name} ({len(cache)} entries)")
    print(
        f"Tokens: {total_prompt_tokens + total_completion_tokens:,} ({total_prompt_tokens:,} prompt, {total_completion_tokens:,} completion)"
    )


if __name__ == "__main__":
    main()
