.PHONY: run eval

run:
	@date +%s > /tmp/.make_run_start
	python fetch.py
	@echo "Execute filtering"
	python groq_tech_filter.py
	rm -f output/news.json
	python curate.py
	@echo "Checking"
	python validate.py
	@echo "Rendering"
	python render.py
	@echo "Total time: $$(( $$(date +%s) - $$(cat /tmp/.make_run_start) ))s"

eval:
	cd eval && python eval_classifier.py
