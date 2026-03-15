Your task is to execute the following instructions:

**INPUT DATA**

- All feed data has already been fetched and is available in per-category JSON files:
  raw_feeds_world.json, raw_feeds_catalunya.json, raw_feeds_podcasts.json, raw_feeds_events.json.
- Do not fetch any URLs yourself. Use only the data in these files.
- Each file contains a "fetched_at" timestamp and a "section" object with an "id" and a list of sources.
  Each source has: name, url, status (ok/blocked/error), optional error_detail, and an items array.
  Each item has: title, link, pubDate, description.
- Use the status and error_detail from each source directly to populate sources_checked in the output.

**SELECTION CRITERIA**
- All the content of all the sections MUST be about technology
- Select up to the top 10 most important world news related to technology published in the last 24 hours
 - Important criteria: prioritize stories covered by multiple sources or with significant impact
 - It is mandatory that they are about technology
- Select up to the top 10 most important Catalan/local news about technology published in the last 72 hours
 - Important criteria: prioritize stories covered by multiple sources or with significant impact
 - It is OK if we cannot get 10 articles, but it is mandatory that they are about technology
 - Reject any article that is primarily about politics, sports, culture, economy, or other non-tech topics — even if it mentions technology in passing
- For podcasts: include all episodes published in the last 15 days from the podcasts section of raw_feeds.json
 - Include any episode published in the last 15 days which is about technology
 - If no episodes were published in the last 15 days, the articles array must be empty
 - Episodes older than 15 days from today must be excluded — check the date carefully before including
 
**OUTPUT FORMAT**
- If the headlines are in Catalan, keep the original headline. Do not rewrite it
- All article titles and summaries must be written in Catalan
 - If you need to translate to Catalan, please do a second step to review the quality of the translation in Catalan language and fix any grammar mistake.
- Summaries should provide an additional angle to the headline and try not to repeat the same content

**RULES FOR THE JSON**
- "generated_at" must be today's date and current time in YYYY-MM-DDTHH:MM format, in Barcelona local time (Europe/Madrid timezone)
- "summary" must be 20 words or fewer, written in Catalan. Count the words carefully — if it exceeds 20 words, shorten it. This limit is strict.
- "url" must be the exact value of the <link> tag inside the RSS <item>. Never derive, reconstruct, or infer a URL from a title, domain pattern, or any other source. If no valid <link> tag exists for an item, skip that article entirely — do not substitute a guessed URL. A URL is only valid if it was explicitly present in the fetched feed content.
- If a URL is relative (starts with /), prepend the source's root domain to make it absolute.
- If a URL passes through a redirect service (e.g. feedproxy.google.com, feedburner.com), follow it and record the final destination URL.
- Skip any article whose URL does not begin with http:// or https://.
- "source" is the publication name (e.g. "TechCrunch", "Ara.cat")
- "date" is the article's publication date in YYYY-MM-DD format, taken from the RSS <pubDate> or <dc:date> tag. Never infer the date from context.
- "time" is the article's publication time in HH:MM format (24h), taken from the same tag. Use "00:00" if not present.
- Output nothing except the JSON object — no markdown, no code fences, no explanation, no HTML, no trailing text
- Filename is news.json
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
          "url": "https://...",
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
          "url": "https://...",
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
          "url": "https://...",
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
          "url": "https://...",
          "source": "Source name",
          "date": "YYYY-MM-DD",
          "time": "HH:MM",
          "summary": "Summary in Catalan, maximum 20 words."
        }
      ]
    }
  ]
}
