# que-es-cou2

News aggregator that fetches RSS feeds, filters tech articles, and renders an HTML page in Catalan. Runs every 4 hours via GitHub Actions and deploys to GitHub Pages at quescou.cat.

## Architecture

- `fetch.py` — fetches all RSS/Atom feeds from `config/sources.yaml`, writes per-category JSON files (`raw_feeds_*.json`)
- `prompts/prompt.md` — instructions for Claude to process feeds into `news.json` (filtering, translation, selection)
- `prompts/tech_topic_filter.md` — instructions for Claude to classify/filter articles by tech topic
- `render.py` — renders `news.json` to `news.html` using `page.jinja2` Jinja2 template, also generates `feed.xml`
- `Makefile` — orchestrates the pipeline via `make run`: `fetch.py` → `claude` (prompts/tech_topic_filter.md) → `claude` (prompts/prompt.md) → `render.py`
- `config/sources.yaml` — all RSS feed sources organized by category: world, catalunya, podcasts, events
- `config/feed_age.json` — per-category max age overrides for feed fetching

## Pipeline

```
config/sources.yaml → fetch.py → raw_feeds_*.json → claude (prompts/tech_topic_filter.md) → claude (prompts/prompt.md) → news.json → render.py → news.html + feed.xml
```

## Categories

- **world** — international tech news (top 10, last 24h)
- **catalunya** — Catalan/local tech news (top 10, last 7 days)
- **podcasts** — Catalan tech podcasts (all episodes within 15 days)
- **events** — Barcelona tech meetups/events

## Key rules (from prompts/prompt.md)

- All output (titles, summaries) must be in Catalan
- Summaries max 20 words
- Only articles with `link` starting with `http://` or `https://`
- Dates taken from RSS pubDate — never inferred
- `generated_at` in Barcelona local time (Europe/Madrid)
- Output is pure JSON, no markdown fences

## Development

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the full pipeline:
```bash
make run
```

The `Makefile` calls `claude --dangerously-skip-permissions -p "Run the prompts/prompt.md task"`.

## CI/CD

GitHub Actions workflow (`.github/workflows/run.yml`) runs on schedule every 4 hours, on push to main, or manually. Deploys to GitHub Pages. Requires `CLAUDE_CONFIG` secret with Claude CLI settings.json content.
