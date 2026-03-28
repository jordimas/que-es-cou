import json
import sys

data = json.load(open("output/news.json"))
total = sum(len(s.get("articles", [])) for s in data.get("sections", []))
if total == 0:
    sys.exit(
        "ERROR: news.json has no articles - Gemini likely failed to produce valid output"
    )
world = next((s for s in data.get("sections", []) if s.get("id") == "world"), None)
world_count = len(world.get("articles", [])) if world else 0
if world_count < 10:
    sys.exit(f"ERROR: world section has {world_count} articles, expected >= 10")
print(f"news.json OK: {total} articles across {len(data['sections'])} sections")
