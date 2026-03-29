Your task is to execute the following instructions:

**INPUT DATA**

- Feed data is provided below in this request from raw_feeds_events_filtered.json or raw_feeds_events.json
- Do not fetch any URLs yourself. Use only the data provided below.
- Each feed contains a "fetched_at" timestamp and a "section" object with an "id" and a list of sources.
  Each source has: name, url, status (ok/blocked/error), optional error_detail, and an items array.
  Each item has: title, pubDate, description, link_id.

**SELECTION CRITERIA**

For events category: include every event whose `pubDate` is within 15 days before `fetched_at`
- Compute the cutoff as: cutoff = fetched_at − 15 days. Include the event if pubDate ≥ cutoff, exclude if pubDate < cutoff
- The sources are already curated — no topic filter needed, include all events in the date window

**OUTPUT FORMAT**

- Exception: If the original headline is already in Catalan (which it likely is for this category), keep the exact original headline. Do not rewrite it.
- Summaries should provide an additional angle to the headline and try not to repeat the same content.

**RULES FOR THE JSON**

- "generated_at" must be today's date and current time in YYYY-MM-DDTHH:MM format, in Barcelona local time (Europe/Madrid timezone)
- "summary" must be 20 words or fewer, written in Catalan. Count the words carefully — if it exceeds 20 words, shorten it. This limit is strict.
- "link_id" must be the exact value of the `link_id` field from the feed item. Never derive, reconstruct, or infer a link_id.
- "source" is the publication name (e.g. "Source name")
- "date" is the event's publication date in YYYY-MM-DD format, taken from the RSS <pubDate> or <dc:date> tag. Never infer the date from context.
- "time" is the event's publication time in HH:MM format (24h), taken from the same tag. Use "00:00" if not present.
- Output nothing except the JSON object — no markdown, no code fences, no explanation, no HTML, no trailing text
- The JSON must strictly follow this schema (sources_checked includes only sources with errors or blocked status):

{
  "generated_at": "YYYY-MM-DDTHH:MM",
  "id": "events",
  "title": "Trobades",
  "sources_checked": [
    {
      "name": "Source name",
      "url": "https://...",
      "articles_found": 0
    }
  ],
  "articles": [
    {
      "title": "Event title",
      "link_id": "xxxx",
      "source": "Source name",
      "date": "YYYY-MM-DD",
      "time": "HH:MM",
      "summary": "Summary in Catalan, maximum 20 words."
    }
  ]
}
