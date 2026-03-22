#!/usr/bin/env python3
"""
Alternative to: claude --dangerously-skip-permissions -p "Run the prompts/tech_topic_filter.md task"
Uses GroqCloud with DeepSeek best model (deepseek-r1-distill-llama-70b).
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

TASK_PROMPT = """Classify each article as tech or not-tech based on its title and description.

INCLUDE an article if it is primarily about:
- Software, apps, platforms, operating systems, programming, web
- Hardware, chips, devices, computers, smartphones, tablets, peripherals, gadgets
- AI, machine learning, robotics, automation, LLMs
- Cybersecurity, hacking, privacy, data breaches, surveillance
- Internet, networking, cloud, data centers, telecom
- Electric vehicles, drones, space tech, biotech, cleantech, renewables
- Tech companies, startups, tech industry, funding rounds, tech products
- Tech regulation, platform policy, digital rights
- Science with direct tech application
- Deals/reviews/news about tech products (phones, laptops, TVs, etc.)

EXCLUDE only if the article clearly is about:
- Pure politics/elections/war with no tech angle
- Sports, food, culture, tourism, entertainment (films/shows not involving tech)
- General economy, real estate, cost of living
- Health/medicine with no device or app angle

When in doubt, INCLUDE the article.

Return ONLY a JSON array of the link_ids of all tech articles. Example: ["c_abc123", "c_def456"]

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
    out_path = Path(os.environ.get("OUT_PATH", base / "tech_topic_filter_new.json"))

    if not world_path.exists() or not catalunya_path.exists():
        print(f"ERROR: input files not found in {base}", file=sys.stderr)
        sys.exit(1)

    world_articles = load_articles(world_path)
    catalunya_articles = load_articles(catalunya_path)

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("ERROR: GROQ_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    client = Groq(api_key=api_key)

    print(
        f"Classifying {len(world_articles)} world + {len(catalunya_articles)} catalunya articles with {GROQ_MODEL}..."
    )

    BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 80))
    total_prompt_tokens = 0
    total_completion_tokens = 0
    last_headers: dict = {}

    def classify_batch(cat: str, articles: list) -> list:
        nonlocal total_prompt_tokens, total_completion_tokens, last_headers
        prompt = TASK_PROMPT.format(
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
        # Extract JSON array from response (model may add explanation or wrap in object)
        start = raw.find("[")
        end = raw.rfind("]")
        if start != -1 and end > start:
            raw = raw[start : end + 1]
        elif raw.startswith("{"):
            # Unwrap {"link_ids": [...]} style
            try:
                obj = json.loads(raw)
                raw = json.dumps(next(iter(obj.values())))
            except Exception:
                pass
        try:
            parsed = json.loads(raw)
            # Handle {"link_ids": [...]} wrapper some models return
            if isinstance(parsed, dict):
                parsed = next(iter(parsed.values()))
            return parsed
        except json.JSONDecodeError:
            # Repair unquoted link_ids: [c_abc, c_def] → ["c_abc", "c_def"]
            repaired = re.sub(r"\b(c_[0-9a-f]+)\b", r'"\1"', raw)
            try:
                return json.loads(repaired)
            except json.JSONDecodeError as e:
                print(
                    f"ERROR: model returned invalid JSON for {cat}: {e}",
                    file=sys.stderr,
                )
                print(raw, file=sys.stderr)
                sys.exit(1)

    result = {}
    for cat, articles in [("world", world_articles), ("catalunya", catalunya_articles)]:
        ids: list[str] = []
        for i in range(0, len(articles), BATCH_SIZE):
            batch = articles[i : i + BATCH_SIZE]
            print(
                f"  {cat} batch {i // BATCH_SIZE + 1}/{(len(articles) + BATCH_SIZE - 1) // BATCH_SIZE} ({len(batch)} articles)..."
            )
            ids.extend(classify_batch(cat, batch))
        result[cat] = ids

    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(
        f"Written {len(result.get('world', []))} world + {len(result.get('catalunya', []))} catalunya IDs to {out_path}"
    )

    total_tokens = total_prompt_tokens + total_completion_tokens
    print(f"\nTokens used this run: {total_tokens:,} (prompt: {total_prompt_tokens:,}, completion: {total_completion_tokens:,})")
    remaining_day = last_headers.get("x-ratelimit-remaining-tokens-day")
    limit_day = last_headers.get("x-ratelimit-limit-tokens-day")
    if remaining_day and limit_day:
        print(f"Daily token quota: {int(remaining_day):,} remaining / {int(limit_day):,} total")


if __name__ == "__main__":
    main()
