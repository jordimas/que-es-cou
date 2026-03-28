#!/usr/bin/env python3
"""
Updated groq_tech_filter.py to strictly follow prompts/tech_topic_filter.md.
"""

import json
import os
import re
import sys
from pathlib import Path

from groq import Groq

GROQ_MODEL = os.environ.get("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

SYSTEM_PROMPT = """You are a news article classifier. You output ONLY a raw JSON array of link_id strings. No keys, no objects, no markdown, no explanation. Just the array.
Correct: ["c_abc123", "c_def456"]
Wrong: {"link_ids": ["c_abc123"]}"""

TECH_TASK_PROMPT = """An article counts as "about technology" if its title and description are primarily about one of these topics:
- Software, apps, platforms, operating systems, programming
- Hardware, chips, devices, computers, smartphones, peripherals
- AI, machine learning, robotics, automation
- Cybersecurity, hacking, privacy, data breaches
- Internet, networking, cloud, data centers
- Electric vehicles, drones, space tech, biotech, cleantech
- Startups, tech companies, tech industry news, funding rounds in tech
- Science with direct tech application
- Catalan language support or localization in tech products, devices, software, or vehicles

An article does NOT count as tech if it is primarily about:
- Politics, elections, government (unless the story is specifically about tech regulation or surveillance tech)
- Sports, culture, entertainment, tourism
- General economy, real estate, cost of living (unless specifically about the tech industry)
- Health or medicine (unless it is about a specific medical device, health app, or biotech product)

When in doubt, exclude the article.

Return ONLY a JSON array of the link_ids of all tech articles.

{category} articles:
{articles_data}
"""

ECONOMY_TASK_PROMPT = """Include articles that are primarily about global economy, finance, markets, business, or trade. 
Exclude sports, culture, and entertainment.

When in doubt, exclude the article.

Return ONLY a JSON array of the link_ids of all economy articles.

{category} articles:
{articles_data}
"""


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

    BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 80))
    total_prompt_tokens = 0
    total_completion_tokens = 0
    last_headers: dict = {}

    def classify_batch(cat: str, articles: list) -> list:
        nonlocal total_prompt_tokens, total_completion_tokens, last_headers
        prompt_tmpl = ECONOMY_TASK_PROMPT if cat == "economy" else TECH_TASK_PROMPT
        prompt = prompt_tmpl.format(
            category=cat,
            articles_data=json.dumps(articles, ensure_ascii=False),
        )
        raw_response = client.with_raw_response.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=4096,
        )
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
            return parsed
        except json.JSONDecodeError:
            repaired = re.sub(r"\b(c_[0-9a-f]+)\b", r'"\1"', raw)
            try:
                return json.loads(repaired)
            except json.JSONDecodeError as e:
                print(f"ERROR: model returned invalid JSON for {cat}: {e}", file=sys.stderr)
                return []

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
            print(f"  {cat} batch {i // BATCH_SIZE + 1}/{(len(articles) + BATCH_SIZE - 1) // BATCH_SIZE}...")
            ids.extend(classify_batch(cat, batch))
        result[cat] = ids

    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Written to {out_path}")


if __name__ == "__main__":
    main()
