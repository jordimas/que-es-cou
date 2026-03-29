Your task is to execute the following instructions:

**INPUT DATA**

- Feed data is provided below in this request from raw_feeds_world_filtered.json
- Do not fetch any URLs yourself. Use only the data provided below.
- Each feed contains a "fetched_at" timestamp and a "section" object with an "id" and a list of sources.
  Each source has: name, url, status (ok/blocked/error), optional error_detail, and an items array.
  Each item has: title, pubDate, description, link_id.

**SELECTION CRITERIA**

For world category, select up to 10 articles of news stories published following this prioritization criteria by order of importance:
- Discard any articles for which pubDate is older than 24 hours
- Count how many sources mention the same story (match by similar title/topic). Sort descending by this count.
- As a tiebreaker, sort by pubDate descending (most recent first)
- Take the top 10 after sorting. When stories tie on both criteria, prefer the one that appears first in the input.

**OUTPUT FORMAT**

- ALL article titles and summaries MUST be translated to and written in Catalan. This is a strict requirement.
- When translating to Catalan, please do a second step to review the quality of the translation in Catalan language and fix any grammar mistakes.
- Summaries should provide an additional angle to the headline and try not to repeat the same content.

**RULES FOR THE JSON**

- "generated_at" must be today's date and current time in YYYY-MM-DDTHH:MM format, in Barcelona local time (Europe/Madrid timezone)
- "summary" must be 20 words or fewer, written in Catalan. Count the words carefully — if it exceeds 20 words, shorten it. This limit is strict.
- "link_id" must be the exact value of the `link_id` field from the feed item. Never derive, reconstruct, or infer a link_id.
- "source" is the publication name (e.g. "TechCrunch")
- "date" is the article's publication date in YYYY-MM-DD format, taken from the RSS <pubDate> or <dc:date> tag. Never infer the date from context.
- "time" is the article's publication time in HH:MM format (24h), taken from the same tag. Use "00:00" if not present.
- Output nothing except the JSON object — no markdown, no code fences, no explanation, no HTML, no trailing text
- The JSON must strictly follow this schema (sources_checked includes only sources with errors or blocked status):

{
  "generated_at": "YYYY-MM-DDTHH:MM",
  "id": "world",
  "title": "Notícies tecnològiques del món",
  "sources_checked": [
    {
      "name": "Source name (e.g. TechCrunch)",
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
