#!/usr/bin/env python3
"""
Alternative to: claude --dangerously-skip-permissions -p "Run the prompts/tech_topic_filter.md task"
Uses GroqCloud with DeepSeek best model (deepseek-r1-distill-llama-70b).
"""

import json
import os
import sys
from pathlib import Path

from groq import Groq

GROQ_MODEL = "deepseek-r1-distill-llama-70b"

SYSTEM_PROMPT = """You are a precise news article classifier. When given instructions, follow them exactly.
Output only valid JSON with no markdown fences, no explanation, no extra text."""

TASK_PROMPT = """Your task is to classify articles from the raw feeds and output a list of article link_ids that pass the tech topic filter.

**TECH TOPIC FILTER**

An article counts as "about technology" if its title and description are primarily about one of these topics:
- Software, apps, platforms, operating systems, programming
- Hardware, chips, devices, computers, smartphones, peripherals
- AI, machine learning, robotics, automation
- Cybersecurity, hacking, privacy, data breaches
- Internet, networking, cloud, data centers
- Electric vehicles, drones, space tech, biotech, cleantech
- Startups, tech companies, tech industry news, funding rounds in tech
- Science with direct tech application

An article does NOT count as tech if it is primarily about:
- Politics, elections, government (unless the story is specifically about tech regulation or surveillance tech)
- Sports, culture, entertainment, tourism
- General economy, real estate, cost of living (unless specifically about the tech industry)
- Health or medicine (unless it is about a specific medical device, health app, or biotech product)

When in doubt, exclude the article.

**TASK**

Classify all articles using the tech topic filter.

Output a JSON object with passing link_ids grouped by category.

**RULES FOR THE JSON**
- Output nothing except the JSON object — no markdown, no code fences, no explanation, no HTML, no trailing text
- The JSON must strictly follow this schema:

{
  "world": ["link_id_1", "link_id_2", ...],
  "catalunya": ["link_id_1", "link_id_2", ...]
}

**INPUT DATA**

world articles:
{world_data}

catalunya articles:
{catalunya_data}
"""


def load_articles(path: Path) -> list[dict]:
    """Extract a flat list of {link_id, title, description} from a raw_feeds_*.json file."""
    data = json.loads(path.read_text())
    articles = []
    for source in data.get("section", {}).get("sources", []):
        for item in source.get("items", []):
            articles.append({
                "link_id": item.get("link_id", ""),
                "title": item.get("title", ""),
                "description": item.get("description", ""),
            })
    return articles


def main():
    base = Path(__file__).parent / "output"
    world_path = base / "raw_feeds_world.json"
    catalunya_path = base / "raw_feeds_catalunya.json"
    out_path = base / "tech_topic_filter_new.json"

    if not world_path.exists() or not catalunya_path.exists():
        print(f"ERROR: input files not found in {base}", file=sys.stderr)
        sys.exit(1)

    world_articles = load_articles(world_path)
    catalunya_articles = load_articles(catalunya_path)

    prompt = TASK_PROMPT.format(
        world_data=json.dumps(world_articles, ensure_ascii=False),
        catalunya_data=json.dumps(catalunya_articles, ensure_ascii=False),
    )

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("ERROR: GROQ_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    client = Groq(api_key=api_key)

    print(f"Classifying {len(world_articles)} world + {len(catalunya_articles)} catalunya articles with {GROQ_MODEL}...")

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )

    raw = response.choices[0].message.content.strip()

    # Strip thinking tags emitted by reasoning models
    if "<think>" in raw:
        end = raw.rfind("</think>")
        raw = raw[end + len("</think>"):].strip() if end != -1 else raw

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: model returned invalid JSON: {e}", file=sys.stderr)
        print(raw, file=sys.stderr)
        sys.exit(1)

    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Written {len(result.get('world', []))} world + {len(result.get('catalunya', []))} catalunya IDs to {out_path}")


if __name__ == "__main__":
    main()
