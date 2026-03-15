Your task is to execute the following instructions:

**INPUT DATA**

- All feed data has already been fetched and is available in per-category JSON files:
  raw_feeds_world.json, raw_feeds_catalunya.json, raw_feeds_podcasts.json, raw_feeds_events.json.
- Do not fetch any URLs yourself. Use only the data in these files.
- Each file contains a "fetched_at" timestamp and a "section" object with an "id" and a list of sources.
  Each source has: name, url, status (ok/blocked/error), optional error_detail, and an items array.
  Each item has: title, link, pubDate, description.
- Use the status and error_detail from each source directly to populate sources_checked in the output.

**TECH TOPIC FILTER**

An article counts as "about technology" if its title and description are primarily about one of these topics:
- Software, apps, platforms, operating systems, programming
- Hardware, chips, devices, computers, smartphones, peripherals
- AI, machine learning, robotics, automation
- Cybersecurity, hacking, privacy, data breaches
- Internet, networking, cloud, data centers
- Electric vehicles, drones, space tech, biotech, cleantech
- Startups, tech companies, tech industry news, funding rounds in tech
- Science with direct tech application

An article does NOT count as tech if it is primarily about:
- Politics, elections, government (unless the story is specifically about tech regulation or surveillance tech)
- Sports, culture, entertainment, tourism
- General economy, real estate, cost of living (unless specifically about the tech industry)
- Health or medicine (unless it is about a specific medical device, health app, or biotech product)

When in doubt, exclude the article.

**SELECTION CRITERIA**
- Select up to 10 of the most important tech news stories published in the last 24 hours
  - Prioritize stories covered by multiple sources or with significant industry impact
  - As a tiebreaker, prefer the most recently published stories
- Select up to the top 10 most important Catalan/local news matching the tech topic filter, published in the last 7 days
  - Prioritize stories covered by multiple sources or with significant impact
  - Select a maxium of 3 articles per source
  - It is OK if fewer than 10 articles are selected
- For podcasts: include every episode whose `pubDate` is within 15 days before `fetched_at` (from raw_feeds_podcasts.json)
  - Compute the cutoff as: cutoff = fetched_at − 15 days. Include the episode if pubDate ≥ cutoff, exclude if pubDate < cutoff
  - The podcast sources are already curated tech podcasts — no topic filter needed, include all episodes in the date window
  - If the episode's `link` does not start with `http://` or `https://`, skip it — do not include it
 
**OUTPUT FORMAT**
- If the headlines are in Catalan, keep the original headline. Do not rewrite it
- All article titles and summaries must be written in Catalan
 - If you need to translate to Catalan, please do a second step to review the quality of the translation in Catalan language and fix any grammar mistake.
- Summaries should provide an additional angle to the headline and try not to repeat the same content

**RULES FOR THE JSON**
- "generated_at" must be today's date and current time in YYYY-MM-DDTHH:MM format, in Barcelona local time (Europe/Madrid timezone)
- "summary" must be 20 words or fewer, written in Catalan. Count the words carefully — if it exceeds 20 words, shorten it. This limit is strict.
- "url" must be the exact value of the `link` field from the feed item. Never derive, reconstruct, or infer a URL.
- Skip any article whose `link` does not start with `http://` or `https://` — no exceptions, no substitutions.
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
