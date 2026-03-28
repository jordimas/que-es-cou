#!/usr/bin/env python3
"""
process.py - Calls Gemini API to process raw feeds into news.json.

Reads prompt.md and raw_feeds_*.json, writes news.json.
Requires GEMINI_API_KEY environment variable.
"""

import json
import os
import sys
from pathlib import Path

import google.generativeai as genai

MODEL = "gemini-3-flash-preview"

output_dir = Path("output")

prompt_text = Path("prompts/prompt.md").read_text(encoding="utf-8")

feed_parts = []
for section_id in ["world", "catalunya", "podcasts", "events", "videos"]:
    path = output_dir / f"raw_feeds_{section_id}.json"
    if path.exists():
        feed_parts.append(
            f"### raw_feeds_{section_id}.json\n{path.read_text(encoding='utf-8')}"
        )

user_content = "\n\n".join(feed_parts)

print(f"Calling Gemini API (model={MODEL}) ...")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    sys.exit("ERROR: GEMINI_API_KEY environment variable not set")

genai.configure(api_key=api_key)
model = genai.GenerativeModel(MODEL)

try:
    response = model.generate_content(
        user_content,
        generation_config=genai.types.GenerationConfig(
            temperature=0,
        ),
        system_instruction=prompt_text,
    )
except Exception as e:
    sys.exit(f"ERROR: Gemini API error: {e}")

output = response.text.strip()

# Strip markdown fences if model added them despite instructions
if output.startswith("```"):
    lines = output.splitlines()
    output = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

try:
    parsed = json.loads(output)
except json.JSONDecodeError as e:
    sys.exit(f"ERROR: Gemini output is not valid JSON: {e}\nOutput:\n{output[:500]}")

output_dir.mkdir(exist_ok=True)
(output_dir / "news.json").write_text(
    json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("output/news.json written")
