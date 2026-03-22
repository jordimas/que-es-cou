#!/usr/bin/env python3
"""
merge_filter.py - Merges tech_topic_filter_new.json (Claude output) with
tech_approved.json (pre-approved articles) into tech_topic_filter.json,
then writes filtered raw feed files containing only approved articles.
"""

import json
from pathlib import Path

output_dir = Path("output")

new_path = output_dir / "tech_topic_filter_new.json"
approved_path = output_dir / "tech_approved.json"
out_path = output_dir / "tech_topic_filter.json"

new_filter = json.loads(new_path.read_text()) if new_path.exists() else {}
approved = json.loads(approved_path.read_text()) if approved_path.exists() else {}

merged = {}
for category in set(list(new_filter.keys()) + list(approved.keys())):
    ids = list(new_filter.get(category, []))
    for link_id in approved.get(category, []):
        if link_id not in ids:
            ids.append(link_id)
    merged[category] = ids

out_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
print(
    f"  Written to '{out_path}' ({sum(len(v) for v in merged.values())} total link_ids)"
)

# Write filtered raw feed files for world and catalunya
for category in ("world", "catalunya"):
    raw_path = output_dir / f"raw_feeds_{category}.json"
    filtered_path = output_dir / f"raw_feeds_{category}_filtered.json"
    if not raw_path.exists():
        continue
    allowed_ids = set(merged.get(category, []))
    data = json.loads(raw_path.read_text())
    filtered_sources = []
    for source in data.get("section", {}).get("sources", []):
        filtered_items = [
            item
            for item in source.get("items", [])
            if item.get("link_id") in allowed_ids
        ]
        filtered_sources.append({**source, "items": filtered_items})
    filtered_data = {
        **data,
        "section": {**data["section"], "sources": filtered_sources},
    }
    filtered_path.write_text(
        json.dumps(filtered_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    total_items = sum(len(s["items"]) for s in filtered_sources)
    print(f"  Written to '{filtered_path}' ({total_items} articles)")
