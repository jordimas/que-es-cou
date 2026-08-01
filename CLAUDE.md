# que-es-cou2

Discontinued news aggregator that fetched RSS feeds, filtered tech articles, and rendered an HTML page in Catalan. GitHub Pages now publishes a static discontinued-project page.

## Historical Architecture

- `fetch.py` — fetches all RSS/Atom feeds from `config/sources.yaml`, writes per-category JSON files (`raw_feeds_*.json`)
- `prompts/curate_*.md` — instructions for Gemini to curate feeds into `news.json` (filtering, translation, selection), one per category
- `prompts/tech_topic_filter.md` — instructions for Gemini to classify/filter articles by tech topic
- `render.py` — renders `news.json` to `news.html` using `page.jinja2` Jinja2 template, also generates `feed.xml`
- `Makefile` — orchestrates the pipeline via `make run`: `fetch.py` → `groq_tech_filter.py` → `curate.py` → `render.py`
- `config/sources.yaml` — all RSS feed sources organized by category: world, catalunya, podcasts, events
- `config/feed_age.json` — per-category max age overrides for feed fetching

## Historical Pipeline

```
config/sources.yaml → fetch.py → raw_feeds_*.json → groq_tech_filter.py (prompts/tech_topic_filter.md) → curate.py (prompts/curate_*.md) → news.json → render.py → news.html + feed.xml
```

## Historical Categories

- **world** — international tech news (top 10, last 24h)
- **catalunya** — Catalan/local tech news (top 10, last 7 days)
- **podcasts** — Catalan tech podcasts (all episodes within 15 days)
- **events** — Barcelona tech meetups/events

## Key rules (from prompts/curate_*.md)

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

The `Makefile` runs `fetch.py`, `groq_tech_filter.py`, `curate.py`, and `render.py` in sequence.

## CI/CD

GitHub Actions workflows deploy a static discontinued-project page to GitHub Pages. Scheduled cron runs and the automated news pipeline are disabled.
