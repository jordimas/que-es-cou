# que-es-cou

News aggregator that fetches RSS feeds, filters tech articles, and renders an HTML page in Catalan. Runs every 4 hours via GitHub Actions and deploys to GitHub Pages.

## Pipeline (`make run`)

```
config/sources.yaml
       │
       ▼
   fetch.py  ──────────────────────────────┬──────────────► raw_feeds_*.json
                                           │               (all content preserved)
                                           │
                                           ▼
                                    tech_approved.json
                                    (pre-approved from
                                     tech: true sources)
                                           │
                                           ├─────────────────────────┐
                                           │                         │
                                           ▼                         ▼
                              groq_tech_filter.py
                           (Groq API classification)
                                           │
                         ┌─────────────────┘
                         │ (merges pre-approved + classified)
                         ▼
              raw_feeds_*_filtered.json
                         │
                         ▼
                    curate_*.md (Gemini)
                         │
                         ▼
                    news.json
                         │
                         ▼
                    render.py
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
     news.html                      feed.xml
```

## Steps

* **fetch.py**
  * Downloads complete RSS feeds applying the age filter
  * Generates `raw_feeds_CATEGORY.json` with all article content
  * Saves `link_id`s of pre-approved articles (from `tech: true` sources) to `tech_approved.json`
  * Preserves all article content (including from tech sources) in raw feeds

* **groq_tech_filter.py**
  * Loads `raw_feeds_*.json` and `tech_approved.json`
  * Classifies non-tech articles using Groq API with `prompts/tech_topic_filter.md`
  * Merges pre-approved articles with newly classified articles
  * Generates `raw_feeds_CATEGORY_filtered.json` containing only approved articles
  * Logs discarded articles to `filtered_tech.log`

* **curate.py**
  * Curates each filtered feed through Gemini API with `prompts/curate_CATEGORY.md`
  * Generates `news.json` with final curated articles in Catalan

* **render.py**
  * Renders `news.json` to `news.html` using Jinja2 template
  * Generates `feed.xml` (RSS feed)

