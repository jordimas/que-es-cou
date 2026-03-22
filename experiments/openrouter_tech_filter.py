#!/usr/bin/env python3
"""
OpenRouter/DeepSeek client for tech topic filtering.
Drop-in replacement for: claude --dangerously-skip-permissions -p "Run the prompts/tech_topic_filter.md task"
"""

import json
import os
import sys
import httpx

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL = "qwen/qwen3-next-80b-a3b-instruct:free"
OUTPUT_DIR = "output"
PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "tech_topic_filter.md")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_prompt(world_data, catalunya_data):
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    # Replace the claude-specific INPUT DATA section (file read instructions)
    # with the actual inlined data for the API call
    input_section = """**INPUT DATA**

Read the following files:
- output/raw_feeds_world.json
- output/raw_feeds_catalunya.json

Do not fetch any URLs yourself. Use only the data in these files."""

    inline_data = f"""**INPUT DATA**

raw_feeds_world.json:
{json.dumps(world_data, ensure_ascii=False)}

raw_feeds_catalunya.json:
{json.dumps(catalunya_data, ensure_ascii=False)}"""

    return template.replace(input_section, inline_data)


def call_openrouter(prompt):
    if not OPENROUTER_API_KEY:
        print("Error: OPENROUTER_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def main():
    world_path = os.path.join(OUTPUT_DIR, "raw_feeds_world.json")
    catalunya_path = os.path.join(OUTPUT_DIR, "raw_feeds_catalunya.json")
    output_path = os.path.join(OUTPUT_DIR, "tech_topic_filter_new.json")

    world_data = load_json(world_path)
    catalunya_data = load_json(catalunya_path)

    prompt = build_prompt(world_data, catalunya_data)
    print(f"Calling {MODEL} via OpenRouter...", file=sys.stderr)
    print(
        f"Prompt size: {len(prompt)} chars / ~{len(prompt) // 4} tokens",
        file=sys.stderr,
    )

    content = call_openrouter(prompt)

    # Validate it's valid JSON with the expected schema
    result = json.loads(content)
    assert "world" in result and "catalunya" in result, (
        "Missing expected keys in response"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(
        f"Written {output_path} ({len(result['world'])} world, {len(result['catalunya'])} catalunya)",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
