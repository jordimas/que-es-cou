Your task is to execute the following instructions:

SELECTION CRITERIA
- News must be from the last 24 hours
- Select the top 5 most important world news related to technology
- Select the top 5 most important Catalan/local news about technology
  - Sources must include: Ara.cat, Vilaweb, LaVanguardia.cat, NacióDigital, plus any other Catalan media
  - All article titles and summaries must be written in Catalan

FETCHING RULES
- Check all news sources for tech stories published today
- When fetching websites, use a standard Mozilla user agent (not Claude's), with curl if needed
- Do not ask permission to run any CLI tool
- Allow fetching any external web content
- If a source is blocked or returns an error, skip it and try the next one

OUTPUT FORMAT
- Output ONLY a valid JSON object — no markdown, no code fences, no explanation, no HTML
- The JSON must strictly follow this schema:

{
  "generated_at": "YYYY-MM-DD",
  "sections": [
    {
      "id": "world",
      "title": "Notícies tecnològiques del món",
      "articles": [
        {
          "title": "Article title in Catalan",
          "url": "https://...",
          "source": "Source name",
          "date": "YYYY-MM-DD",
          "summary": "Summary in Catalan, maximum 50 words."
        }
      ]
    },
    {
      "id": "catalunya",
      "title": "Notícies tecnològiques de Catalunya",
      "articles": [
        {
          "title": "Article title in Catalan",
          "url": "https://...",
          "source": "Source name",
          "date": "YYYY-MM-DD",
          "summary": "Summary in Catalan, maximum 50 words."
        }
      ]
    }
  ]
}

RULES FOR THE JSON
- "generated_at" must be today's date in YYYY-MM-DD format
- Each section must contain exactly 5 articles
- "summary" must be 50 words or fewer, written in Catalan
- "url" must be the direct link to the article
- "source" is the publication name (e.g. "TechCrunch", "Ara.cat")
- "date" is the article's publication date
- Output nothing except the JSON object
- Filename is news.json
