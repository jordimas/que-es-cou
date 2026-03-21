#!/usr/bin/env python3
"""
merge_filter.py - Merges tech_topic_filter_new.json (Claude output) with
tech_approved.json (pre-approved articles) into tech_topic_filter.json.
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
print(f"  Written to '{out_path}' ({sum(len(v) for v in merged.values())} total link_ids)")
