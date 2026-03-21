.PHONY: run eval

run:
	@date +%s > /tmp/.make_run_start
	python fetch.py
	@echo "Execute filtering"
	claude --dangerously-skip-permissions -p "Run the prompts/tech_topic_filter.md task"
	python merge_filter.py
	@echo "Execute prompt.md"
	rm -f output/news.json
	claude --dangerously-skip-permissions -p "Run the prompts/prompt.md task"
	@echo "Checking"
	python -c "\
import json, sys; \
data = json.load(open('output/news.json')); \
total = sum(len(s.get('articles', [])) for s in data.get('sections', [])); \
sys.exit('ERROR: news.json has no articles - Claude likely failed to produce valid output') if total == 0 else print(f'news.json OK: {total} articles across {len(data[\"sections\"])} sections')"
	@echo "Rendering"
	python render.py
	@echo "Total time: $$(( $$(date +%s) - $$(cat /tmp/.make_run_start) ))s"

eval:
	cd eval && python eval_classifier.py
