Your task is to execute the following instructions:

**INPUT DATA**

- All feed data has already been fetched and is available in per-category JSON files:
  - output/raw_feeds_world_filtered.json -> category world
  - output/raw_feeds_catalunya_filtered.json -> category catalunya
  - output/raw_feeds_podcasts.json -> category podcasts
  - output/raw_feeds_events.json -> category events
  - output/raw_feeds_videos.json -> category videos
- Do not fetch any URLs yourself. Use only the data in these files.
- Each file contains a "fetched_at" timestamp and a "section" object with an "id" and a list of sources.
  Each source has: name, url, status (ok/blocked/error), optional error_detail, and an items array.
  Each item has: title, link, pubDate, description.
- Use the status and error_detail from each source directly to populate sources_checked in the output.

**SELECTION CRITERIA**
- For world category, select up to 10 articles of news stories published following this prioritization criteria by order of importance:
  - Discard any articles for which pubDate is older than 24 hours
  - Count how many sources mention the same story (match by similar title/topic). Sort descending by this count.
  - As a tiebreaker, sort by pubDate descending (most recent first)
  - Take the top 10 after sorting. When stories tie on both criteria, prefer the one that appears first in the input.
- For catalunya category, select up to 10 articles of news stories published following this prioritization criteria by order of importance:
  - Discard any article which is not in Catalan language
  - Discard any articles for which pubDate is older than 7 days
  - Prioritize stories covered by multiple sources
  - Prioritize stores with impact for society and end-users
  - Hard limit: never include more than 3 articles from the same source, skip any further articles from that source.
  - It is OK if fewer than 10 articles are selected
- For podcasts category: include every episode whose `pubDate` is within 15 days before `fetched_at`
  - Compute the cutoff as: cutoff = fetched_at − 15 days. Include the episode if pubDate ≥ cutoff, exclude if pubDate < cutoff
  - The sources are already curated tech podcasts — no topic filter needed, include all episodes in the date window
  - If the episode's `link` does not start with `http://` or `https://`, skip it — do not include it
- For events category: include every event whose `pubDate` is within 15 days before `fetched_at`
  - Compute the cutoff as: cutoff = fetched_at − 15 days. Include the episode if pubDate ≥ cutoff, exclude if pubDate < cutoff
  - The podcast sources are already curated — no topic filter needed, include all episodes in the date window
- For videos category: include every video whose `pubDate` is within 15 days before `fetched_at`
  - Compute the cutoff as: cutoff = fetched_at − 15 days. Include the video if pubDate ≥ cutoff, exclude if pubDate < cutoff
  - The sources are already curated Catalan YouTube channels — no topic filter needed, include all videos in the date window
  - If the video's `link` does not start with `http://` or `https://`, skip it

 
**OUTPUT FORMAT**
- If the headlines are in Catalan, keep the original headline. Do not rewrite it
- All article titles and summaries must be written in Catalan
 - If you need to translate to Catalan, please do a second step to review the quality of the translation in Catalan language and fix any grammar mistake.
- Summaries should provide an additional angle to the headline and try not to repeat the same content

**RULES FOR THE JSON**
- "generated_at" must be today's date and current time in YYYY-MM-DDTHH:MM format, in Barcelona local time (Europe/Madrid timezone)
- "summary" must be 20 words or fewer, written in Catalan. Count the words carefully — if it exceeds 20 words, shorten it. This limit is strict.
- "link_id" must be the exact value of the `link_id` field from the feed item. Never derive, reconstruct, or infer a link_id.
- Skip any article whose `link` does not start with `http://` or `https://` — no exceptions, no substitutions.
- "source" is the publication name (e.g. "TechCrunch", "Ara.cat")
- "date" is the article's publication date in YYYY-MM-DD format, taken from the RSS <pubDate> or <dc:date> tag. Never infer the date from context.
- "time" is the article's publication time in HH:MM format (24h), taken from the same tag. Use "00:00" if not present.
- Output nothing except the JSON object — no markdown, no code fences, no explanation, no HTML, no trailing text
- Filename is output/news.json
- The JSON must strictly follow this schema:

{
  "generated_at": "YYYY-MM-DDTHH:MM",
  "sections": [
    {
      "id": "world",
      "title": "Notícies tecnològiques del món",
      "sources_checked": [
        {
          "name": "Source name (e.g. TechCrunch)",
          "url": "https://...",
          "status": "ok | blocked | error",
          "error_detail": "Exact error message if status is error or blocked, omit field if status is ok",
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
    },
    {
      "id": "catalunya",
      "title": "Notícies tecnològiques de Catalunya",
      "sources_checked": [
        {
          "name": "Source name (e.g. Ara.cat)",
          "url": "https://...",
          "status": "ok | blocked | error",
          "error_detail": "Exact error message if status is error or blocked, omit field if status is ok",
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
    },
    {
      "id": "podcasts",
      "title": "Podcasts en català sobre tecnologia",
      "sources_checked": [
        {
          "name": "Podcast name",
          "url": "https://...",
          "status": "ok | blocked | error",
          "error_detail": "Exact error message if status is error or blocked, omit field if status is ok",
          "articles_found": 0
        }
      ],
      "articles": [
        {
          "title": "Episode title",
          "link_id": "xxxx",
          "source": "Podcast name",
          "date": "YYYY-MM-DD",
          "time": "HH:MM",
          "summary": "Summary in Catalan, maximum 20 words."
        }
      ]
    },
    {
      "id": "events",
      "title": "Trobades",
      "sources_checked": [
        {
          "name": "Source name",
          "url": "https://...",
          "status": "ok | blocked | error",
          "error_detail": "Exact error message if status is error or blocked, omit field if status is ok",
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
    },
    {
      "id": "videos",
      "title": "Vídeos en català sobre tecnologia",
      "sources_checked": [
        {
          "name": "Channel name",
          "url": "https://...",
          "status": "ok | blocked | error",
          "error_detail": "Exact error message if status is error or blocked, omit field if status is ok",
          "articles_found": 0
        }
      ],
      "articles": [
        {
          "title": "Video title",
          "link_id": "xxxx",
          "source": "Channel name",
          "date": "YYYY-MM-DD",
          "time": "HH:MM",
          "summary": "Summary in Catalan, maximum 20 words."
        }
      ]
    }
  ]
}
