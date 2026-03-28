.PHONY: run eval

run:
	@date +%s > /tmp/.make_run_start
	python fetch.py
	@echo "Execute filtering"
	gemini --yolo --model gemini-3-flash-preview -p "Run the prompts/tech_topic_filter.md task"
	python merge_filter.py
	@echo "Execute prompt.md"
	rm -f output/news.json
	gemini --yolo --model gemini-3-flash-preview -p "Run the prompts/prompt.md task"
	@echo "Checking"
	python validate.py
	@echo "Rendering"
	python render.py
	@echo "Total time: $$(( $$(date +%s) - $$(cat /tmp/.make_run_start) ))s"

eval:
	cd eval && python eval_classifier.py
