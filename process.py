#!/usr/bin/env python3
"""
process.py - Calls Claude API with temperature=0 to process raw feeds into news.json.

Reads prompt.md and raw_feeds_*.json, writes news.json.
Requires ANTHROPIC_API_KEY environment variable.
"""

import json
import os
import sys
from pathlib import Path

import anthropic

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 16000

output_dir = Path("output")

prompt_text = Path("prompt.md").read_text(encoding="utf-8")

feed_parts = []
for section_id in ["world", "catalunya", "podcasts", "events", "videos"]:
    path = output_dir / f"raw_feeds_{section_id}.json"
    if path.exists():
        feed_parts.append(f"### raw_feeds_{section_id}.json\n{path.read_text(encoding='utf-8')}")

user_content = "\n\n".join(feed_parts)

print(f"Calling Claude API (temperature=0, model={MODEL}) ...")

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment

try:
    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        temperature=0,
        system=prompt_text,
        messages=[{"role": "user", "content": user_content}],
    )
except anthropic.APIError as e:
    sys.exit(f"ERROR: Claude API error: {e}")

output = message.content[0].text.strip()

# Strip markdown fences if model added them despite instructions
if output.startswith("```"):
    lines = output.splitlines()
    output = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

try:
    parsed = json.loads(output)
except json.JSONDecodeError as e:
    sys.exit(f"ERROR: Claude output is not valid JSON: {e}\nOutput:\n{output[:500]}")

output_dir.mkdir(exist_ok=True)
(output_dir / "news.json").write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
print("output/news.json written")
