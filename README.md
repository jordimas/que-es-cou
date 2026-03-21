# que-es-cou

News aggregator that fetches RSS feeds, filters tech articles, and renders an HTML page in Catalan. Runs every 4 hours via GitHub Actions and deploys to GitHub Pages.

## Pipeline (`make run`)

```
config/sources.yaml
       │
       ▼
   fetch.py  ──────────────────────────► raw_feeds_*.json
                                                │
                                                ▼
                                   tech_topic_filter.md
                                                │
                                                ▼
                                       merge_filter.py ──► raw_feeds_*_filtered.json
                                                                       │
                                                                       ▼
                                                                  prompt.md
                                                                       │
                                                                       ▼
                                                                  news.json
                                                                       │
                                                                       ▼
                                                                  render.py
                                                                       │
                                                    ┌──────────────────┴──────────────────┐
                                                    ▼                                     ▼
                                               news.html                              feed.xml
```

## Steps

| Step | Script / Tool | I/O | Role |
|------|--------------|-----|------|
| 1. Fetch feeds | `fetch.py` | `sources.yaml` → `raw_feeds_*.json` | Downloads all RSS/Atom feeds and writes one JSON file per category (world, catalunya, podcasts, events) |
| 2. Tech topic filter | `tech_topic_filter.md` | `raw_feeds_*.json` → `tech_topic_filter.json` | Classifies each article by tech topic and marks non-tech articles for removal |
| 3. Merge filter | `merge_filter.py` | `raw_feeds_*.json` + `tech_topic_filter.json` → `raw_feeds_*_filtered.json` | Merges filter results and writes filtered feed files containing only approved articles |
| 4. Process & translate | `prompt.md` | `raw_feeds_*_filtered.json` → `news.json` | Selects the top articles per category, translates titles and summaries to Catalan, and structures the final output |
| 5. Validate | `validate.py` | `news.json` → — | Checks that `news.json` contains at least one article; fails fast if the previous step produced empty output |
| 6. Render | `render.py` | `news.json` + `page.jinja2` → `news.html`, `feed.xml` | Renders the Jinja2 HTML page and Atom feed for GitHub Pages |
