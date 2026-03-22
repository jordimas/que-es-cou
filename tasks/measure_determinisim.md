
Goal: your goal is to measure how deterministic is the system end to end determined by the articles written in news.json

# How
- Pipeline execution
  - Look at the 'make run' Makefile task to understand the parts of the pipeline
  - Reuse the same pre-fetched raw_feeds_*.json files across all 3 runs, not re-fetch each time.
  - Run the system 3 times in parallel in separate directories
- Measure how deterministic is:
  - tech_topic filtering in the pipeline
    - How many articles are the same selected across runs
  - article selection done by prompt.md and written in news.json
    - How many articles are the same selected across runs
 - Show a table at the end with the results and conclusions

