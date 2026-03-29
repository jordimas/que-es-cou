#!/usr/bin/env python3
"""
gemini_tech_filter.py - Classifies articles by tech topic using Gemini API.

Reads prompts/tech_topic_filter.md and raw_feeds_*.json files, calls Gemini API,
writes tech_topic_filter_new.json with approved link_ids per category.

Requires GEMINI_API_KEY environment variable.
"""

import json
import os
import re
import sys
from pathlib import Path

import google.generativeai as genai

MODEL = "gemini-3-flash-preview"
output_dir = Path("output")


def load_articles(path: Path) -> list[dict]:
    """Extract a flat list of {link_id, title, description} from a raw_feeds_*.json file."""
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    articles = []
    for source in data.get("section", {}).get("sources", []):
        for item in source.get("items", []):
            # Strip HTML tags from description
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


def classify_category(client, category: str, articles: list[dict], prompt_text: str) -> list[str]:
    """Classify articles in a category using Gemini API."""
    if not articles:
        return []

    # Build the data string for this category
    articles_data = json.dumps(articles, ensure_ascii=False)

    # Customize prompt based on category
    if category == "economy":
        category_instruction = """For the economy category, include articles that are primarily about global economy, finance, markets, business, or trade. Exclude sports, culture, and entertainment."""
    else:
        category_instruction = f"""For the {category} category, use the tech topic filter rules."""

    user_message = f"""{prompt_text}

{category_instruction}

Classify all articles below. Output ONLY a JSON array of link_ids that pass the filter. No explanations, no markdown.

{category} articles:
{articles_data}"""

    try:
        response = client.generate_content(
            user_message,
            generation_config=genai.types.GenerationConfig(temperature=0),
        )
    except Exception as e:
        print(f"ERROR: Gemini API error for {category}: {e}", file=sys.stderr)
        return []

    output = response.text.strip()

    # Extract JSON array from response (handle markdown fences, think tags, etc.)
    if output.startswith("```"):
        lines = output.splitlines()
        output = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

    # Handle model thinking tags
    if "<think>" in output:
        end = output.rfind("</think>")
        output = output[end + len("</think>") :].strip() if end != -1 else output

    # Extract JSON array
    start = output.find("[")
    end = output.rfind("]")
    if start != -1 and end > start:
        output = output[start : end + 1]

    try:
        parsed = json.loads(output)
        if isinstance(parsed, dict):
            # If accidentally a dict, try to extract the first value
            parsed = next(iter(parsed.values()), [])
        if not isinstance(parsed, list):
            parsed = []
        return parsed
    except json.JSONDecodeError:
        # Try to repair common JSON errors (unquoted strings)
        repaired = re.sub(r"\b(c_[0-9a-f]+)\b", r'"\1"', output)
        try:
            parsed = json.loads(repaired)
            if isinstance(parsed, dict):
                parsed = next(iter(parsed.values()), [])
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse JSON for {category}: {e}\nOutput: {output[:200]}", file=sys.stderr)
            return []


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("ERROR: GEMINI_API_KEY environment variable not set")

    prompt_text = Path("prompts/tech_topic_filter.md").read_text(encoding="utf-8")

    genai.configure(api_key=api_key)
    client = genai.GenerativeModel(MODEL)

    result = {}
    categories = {
        "world": output_dir / "raw_feeds_world.json",
        "economy": output_dir / "raw_feeds_economy.json",
        "catalunya": output_dir / "raw_feeds_catalunya.json",
    }

    for category, path in categories.items():
        if not path.exists():
            print(f"Skipping {category}: {path} not found")
            result[category] = []
            continue

        articles = load_articles(path)
        print(f"Classifying {len(articles)} {category} articles...")

        link_ids = classify_category(client, category, articles, prompt_text)
        result[category] = link_ids
        print(f"  {category}: {len(link_ids)} articles passed filter")

    output_dir.mkdir(exist_ok=True)
    out_path = output_dir / "tech_topic_filter_new.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Written to {out_path}")


if __name__ == "__main__":
    main()
