Your task is to execute the following instructions:

**INPUT DATA**

- Feed data is provided below in this request from raw_feeds_catalunya_filtered.json
- Each feed contains a "fetched_at" timestamp and a "section" object with an "id" and a list of sources.
  Each source has: name, url, and an items array.
  Each item has: title, pubDate, description, link_id.

**SELECTION CRITERIA**

For catalunya category, select up to 10 articles of news stories published following this prioritization criteria by order of importance:
- Discard any article which is not in Catalan language
- Prioritize stories covered by multiple sources
- Prioritize stories with impact for society and end-users
- If there are multiple articles that are very similar, select only the most recent one based on pubDate
- Hard limit: never include more than 3 articles from the same source, skip any further articles from that source.
- As a final tiebreaker, prefer the article that appears first in the input.
- It is OK if fewer than 10 articles are selected

**OUTPUT FORMAT**

- Summaries should provide an additional angle to the headline and try not to repeat the same content.

**RULES FOR THE JSON**

- "generated_at" must be today's date and current time in YYYY-MM-DDTHH:MM format, in Barcelona local time (Europe/Madrid timezone)
- "summary" must be 20 words or fewer, written in Catalan. Count the words carefully — if it exceeds 20 words, shorten it. This limit is strict.
- "link_id" must be the exact value of the `link_id` field from the feed item. Never derive, reconstruct, or infer a link_id.
- "source" is the publication name (e.g. "Ara.cat")
- "date" is the article's publication date in YYYY-MM-DD format, taken from the RSS <pubDate> or <dc:date> tag. Never infer the date from context.
- "time" is the article's publication time in HH:MM format (24h), taken from the same tag. Use "00:00" if not present.
- Output nothing except the JSON object — no markdown, no code fences, no explanation, no HTML, no trailing text
- The JSON must strictly follow this schema:

{
  "generated_at": "YYYY-MM-DDTHH:MM",
  "id": "catalunya",
  "title": "Notícies tecnològiques de Catalunya",
  "sources_checked": [
    {
      "name": "Source name (e.g. Ara.cat)",
      "url": "https://...",
      "articles_found": 0
    }
  ],
  "articles": [
    {
      "title": "Article title in Catalan",
      "link_id": "xxxx",
      "source": "Source name",
      "date": "YYYY-MM-DD",
      "time": "HH:MM",
      "summary": "Summary in Catalan, maximum 20 words."
    }
  ]
}
