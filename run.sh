set -e
python fetch.py
claude --dangerously-skip-permissions -p "Run the prompt.md task"
python -c "
import json, sys
try:
    data = json.load(open('news.json'))
except Exception as e:
    sys.exit(f'ERROR: news.json missing or invalid: {e}')
total = sum(len(s.get('articles', [])) for s in data.get('sections', []))
if total == 0:
    sys.exit('ERROR: news.json has no articles - Claude likely failed to produce valid output')
print(f'news.json OK: {total} articles across {len(data[\"sections\"])} sections')
"
python render.py
