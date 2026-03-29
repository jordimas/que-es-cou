Your task is to execute the following instructions:

**INPUT DATA**

- Feed data is provided below in this request from raw_feeds_videos_filtered.json or raw_feeds_videos.json
- Do not fetch any URLs yourself. Use only the data provided below.
- Each feed contains a "fetched_at" timestamp and a "section" object with an "id" and a list of sources.
  Each item has: title, pubDate, description, link_id.
- Include ONLY sources with errors or blocked status in sources_checked. Omit sources with status="ok" and articles_found=0.

**SELECTION CRITERIA**

For videos category: include every video whose `pubDate` is within 15 days before `fetched_at`
- Compute the cutoff as: cutoff = fetched_at − 15 days. Include the video if pubDate ≥ cutoff, exclude if pubDate < cutoff
- The sources are already curated Catalan YouTube channels — no topic filter needed, include all videos in the date window

**OUTPUT FORMAT**

- Exception: If the original headline is already in Catalan (which it should be for this category), keep the exact original headline. Do not rewrite it.
- Summaries should provide an additional angle to the headline and try not to repeat the same content.

**RULES FOR THE JSON**

- "generated_at" must be today's date and current time in YYYY-MM-DDTHH:MM format, in Barcelona local time (Europe/Madrid timezone)
- "summary" must be 20 words or fewer, written in Catalan. Count the words carefully — if it exceeds 20 words, shorten it. This limit is strict.
- "link_id" must be the exact value of the `link_id` field from the feed item. Never derive, reconstruct, or infer a link_id.
- "source" is the channel name (e.g. "Channel name")
- "date" is the video's publication date in YYYY-MM-DD format, taken from the RSS <pubDate> or <dc:date> tag. Never infer the date from context.
- "time" is the video's publication time in HH:MM format (24h), taken from the same tag. Use "00:00" if not present.
- Output nothing except the JSON object — no markdown, no code fences, no explanation, no HTML, no trailing text
- The JSON must strictly follow this schema (sources_checked includes only sources with errors or blocked status):

{
  "generated_at": "YYYY-MM-DDTHH:MM",
  "id": "videos",
  "title": "Vídeos en català sobre tecnologia",
  "sources_checked": [
    {
      "name": "Channel name",
      "url": "https://...",
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
