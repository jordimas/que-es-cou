# que-es-cou2

News aggregator that fetches RSS feeds, filters tech articles, and renders an HTML page in Catalan. Runs every 4 hours via GitHub Actions and deploys to GitHub Pages at quescou.cat.

## Architecture

- `fetch.py` — fetches all RSS/Atom feeds from `sources.yaml`, writes per-category JSON files (`raw_feeds_*.json`)
- `prompt.md` — instructions for Claude to process feeds into `news.json` (filtering, translation, selection)
- `render.py` — renders `news.json` to `news.html` using `page.html` Jinja2 template, also generates `feed.xml`
- `run.sh` — orchestrates the pipeline: `fetch.py` → `claude` (prompt.md task) → `render.py`
- `sources.yaml` — all RSS feed sources organized by category: world, catalunya, podcasts, events

## Pipeline

```
sources.yaml → fetch.py → raw_feeds_*.json → claude (prompt.md) → news.json → render.py → news.html + feed.xml
```

## Categories

- **world** — international tech news (top 10, last 24h)
- **catalunya** — Catalan/local tech news (top 10, last 7 days)
- **podcasts** — Catalan tech podcasts (all episodes within 15 days)
- **events** — Barcelona tech meetups/events

## Key rules (from prompt.md)

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
bash run.sh
```

The `run.sh` calls `claude --dangerously-skip-permissions -p "Run the prompt.md task"`.

## CI/CD

GitHub Actions workflow (`.github/workflows/run.yml`) runs on schedule every 4 hours, on push to main, or manually. Deploys to GitHub Pages. Requires `CLAUDE_CONFIG` secret with Claude CLI settings.json content.
