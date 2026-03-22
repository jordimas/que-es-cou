import json
import sys

data = json.load(open("output/news.json"))
total = sum(len(s.get("articles", [])) for s in data.get("sections", []))
if total == 0:
    sys.exit(
        "ERROR: news.json has no articles - Claude likely failed to produce valid output"
    )
print(f"news.json OK: {total} articles across {len(data['sections'])} sections")
