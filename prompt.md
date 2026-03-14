Your task is to execute the following instructions:

**FETCHING CRITERIA**

- What to fetch
  - Check all news sources for tech stories published today
  - For world news, fetch 50 articles for at least 10 technology sources
    - These should include TechCrunch, Ars Technica, The Verge, Wired, MIT Tech Review
  - For Catalan news, fetch 50 articles for at least 10 sources
    - Include all the sources that you are aware of in Catalan language
    - Make sure that include: Ara.cat, Vilaweb, www.laVanguardia.com/catala, NacióDigital, 324.cat, Softcatalà
- How
  - When fetching websites, use a standard Mozilla user agent (not Claude's), with curl if needed
  - If a source is blocked or returns an error, skip it and try the next one
  - Keep track of every source URL you attempt to fetch, and record whether it succeeded or failed
- Permissions
  - Do not ask permission to run any CLI tool
  - Allow fetching any external web content

**SELECTION CRITERIA**
- News must be from the last 24 hours
- Select the top 10 most important world news related to technology
- Select the top 10 most important Catalan/local news about technology 

**OUTPUT FORMAT**
- If the headlines are in Catalan, keep the original headline. Do not rewrite it
- All article titles and summaries must be written in Catalan

**RULES FOR THE JSON**
- "generated_at" must be today's date and current time in YYYY-MM-DDTHH:MM format, in Barcelona local time (Europe/Madrid timezone)
- "summary" must be 20 words or fewer, written in Catalan
- "url" must be the direct link to the article
- "source" is the publication name (e.g. "TechCrunch", "Ara.cat")
- "date" is the article's publication date
- "time" is the article's publication time in HH:MM format (24h); use "00:00" if unknown
- Output nothing except the JSON object
- Filename is news.json

- Output ONLY a valid JSON object — no markdown, no code fences, no explanation, no HTML
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
    }
  ]
}


