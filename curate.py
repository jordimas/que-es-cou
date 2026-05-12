#!/usr/bin/env python3
"""
curate.py - Curates raw feeds into news.json using Groq API.

Loads raw_feeds_*_filtered.json files (pre-filtered by tech topic) and calls
Groq API separately for each section with prompts/curate_*.md instructions
to generate news.json with all sections combined.

Requires GROQ_API_KEY environment variable.
"""

import json
import os
import sys
import time
from pathlib import Path

from groq import Groq, InternalServerError

GROQ_MODEL = os.environ.get("GROQ_MODEL", "qwen/qwen3-32b")
output_dir = Path("output")
SECTIONS = ["world", "economy", "catalunya", "podcasts", "events", "videos"]


def load_section_feed(section_id):
    path = output_dir / f"raw_feeds_{section_id}_filtered.json"
    if not path.exists():
        path = output_dir / f"raw_feeds_{section_id}.json"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def process_section(section_id, client):
    prompt_file = Path("prompts") / f"curate_{section_id}.md"

    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    feed_data = load_section_feed(section_id)
    if not feed_data:
        print(f"Warning: No feed file found for {section_id}, skipping")
        return None

    prompt_text = prompt_file.read_text(encoding="utf-8")

    input_size_kb = len(feed_data.encode("utf-8")) / 1024
    feed_json = json.loads(feed_data)
    item_count = sum(
        len(s.get("items", [])) for s in feed_json.get("section", {}).get("sources", [])
    )
    print(f"Processing {section_id} (input: {input_size_kb:.1f} KB, {item_count} items)...")

    start_time = time.time()
    for attempt in range(5):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": prompt_text},
                    {"role": "user", "content": feed_data},
                ],
                temperature=0.0,
                max_tokens=32768,
            )
            break
        except InternalServerError as e:
            if attempt == 4:
                raise Exception(f"Groq API error for {section_id}: {e}")
            wait = 20 * (2 ** attempt)
            print(f"  [retry] Groq 503 for {section_id} (attempt {attempt + 1}/5), waiting {wait}s: {e}")
            time.sleep(wait)
        except Exception as e:
            if attempt == 4:
                raise Exception(f"Groq API error for {section_id}: {e}")
            wait = 20 * (2 ** attempt)
            print(f"  [retry] error for {section_id} (attempt {attempt + 1}/5), waiting {wait}s: {e}")
            time.sleep(wait)
    api_time = time.time() - start_time

    token_usage = {}
    if response.usage:
        token_usage = {
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
        }

    output = response.choices[0].message.content.strip()

    # Strip <think> blocks from reasoning models
    if "<think>" in output:
        end = output.rfind("</think>")
        output = output[end + len("</think>"):].strip() if end != -1 else output

    (output_dir / f"debug_raw_output_{section_id}.txt").write_text(output, encoding="utf-8")

    # Strip markdown fences if model added them despite instructions
    if output.startswith("```"):
        lines = output.splitlines()
        output = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

    try:
        parsed = json.loads(output)
    except json.JSONDecodeError as e:
        raise Exception(
            f"Groq output is not valid JSON for {section_id}: {e}\nOutput:\n{output[:500]}"
        )

    parsed["_meta"] = {
        "input_size_kb": input_size_kb,
        "api_time_s": api_time,
        "tokens": token_usage,
    }

    return parsed


def main():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        sys.exit("ERROR: GROQ_API_KEY environment variable not set")

    client = Groq(api_key=api_key)
    output_dir.mkdir(exist_ok=True)

    sections_data = []

    for section_id in SECTIONS:
        try:
            section_result = process_section(section_id, client)
            if section_result:
                sections_data.append(section_result)
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)

    if not sections_data:
        sys.exit("ERROR: No sections processed successfully")

    metadata = {}
    for section in sections_data:
        if "_meta" in section:
            meta = section.pop("_meta")
            metadata[section.get("id", "unknown")] = meta

    combined = {
        "generated_at": sections_data[0].get("generated_at"),
        "sections": sections_data,
    }

    (output_dir / "news.json").write_text(
        json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("output/news.json written\n")

    print("=" * 85)
    print("Processing Summary:")
    print("=" * 85)
    total_time = 0
    total_input_tokens = 0
    total_output_tokens = 0
    for section_id in SECTIONS:
        if section_id in metadata:
            meta = metadata[section_id]
            size = meta["input_size_kb"]
            api_time = meta["api_time_s"]
            tokens = meta.get("tokens", {})
            input_tokens = tokens.get("input_tokens", 0)
            output_tokens = tokens.get("output_tokens", 0)
            total_tokens = input_tokens + output_tokens
            total_time += api_time
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            print(
                f"{section_id:12s} | Input: {size:7.1f} KB | Time: {api_time:6.1f}s | Tokens: {total_tokens:6d} (in: {input_tokens}, out: {output_tokens})"
            )
    print("=" * 85)
    total_all_tokens = total_input_tokens + total_output_tokens
    print(
        f"{'TOTAL':12s} | {'':<22s} | Time: {total_time:6.1f}s | Tokens: {total_all_tokens:6d} (in: {total_input_tokens}, out: {total_output_tokens})"
    )
    print("=" * 85)


if __name__ == "__main__":
    main()
