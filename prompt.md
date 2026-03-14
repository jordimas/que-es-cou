Your task is to execute the following instructions:

**FETCHING CRITERIA**

- What to fetch
  - Check all news sources for tech stories published today published in the last 48 hours
  - For world news, fetch 50 articles for at least 30 technology sources
    - Use these exact RSS URLs in the LIST OF WORLD SOURCES section
  - For Catalan news, fetch 50 articles for at least 20 sources published in the last 48 hours
    - Include all the sources that you are aware of in Catalan language
    - Make sure to include the following, using LIST OF CATALAN SOURCES section:
- How
  - When fetching websites, use a standard Mozilla user agent (not Claude's), with curl if needed
  - If a source is blocked or returns an error, skip it and try the next one
  - Keep track of every source URL you attempt to fetch, and record whether it succeeded or failed
- Permissions
  - Do not ask permission to run any CLI tool
  - Allow fetching any external web content

**SELECTION CRITERIA**
- News have to be published in the last 48 hours
- Select up to the top 10 most important world news related to technology
 - Important criteria: voted, cited, or popular across different media
- Select up to the top 10 most important Catalan/local news about technology 
 - Important locally: Catalan culture, language, local companies or citizens.
 
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

**LIST OF WORLD SOURCES**
- TechCrunch: https://techcrunch.com/feed/
- Ars Technica: https://feeds.arstechnica.com/arstechnica/technology-lab
- The Verge: https://www.theverge.com/rss/index.xml
- Wired: https://www.wired.com/feed/rss
- MIT Technology Review: https://www.technologyreview.com/feed/
- Engadget: https://www.engadget.com/rss.xml
- ZDNet: https://www.zdnet.com/news/rss.xml
- VentureBeat: https://feeds.feedburner.com/venturebeat/SZYF
- CNET: https://www.cnet.com/rss/news/
- MacRumors: https://feeds.macrumors.com/MacRumors-All
- 9to5Mac: https://9to5mac.com/feed/
- 9to5Google: https://9to5google.com/feed/
- Android Authority: https://www.androidauthority.com/feed/
- Tom's Hardware: https://www.tomshardware.com/feeds/all
- AnandTech: https://www.anandtech.com/rss/
- PCWorld: https://www.pcworld.com/index.rss
- Digital Trends: https://www.digitaltrends.com/feed/
- The Guardian Tech: https://www.theguardian.com/technology/rss
- BBC Technology: https://feeds.bbci.co.uk/news/technology/rss.xml
- NYT Technology: https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml
- Bloomberg Technology: https://feeds.bloomberg.com/technology/news.rss
- Axios: https://www.axios.com/feeds/feed.rss
- Wall Street Journal Tech: https://feeds.a.dj.com/rss/RSSWSJD.xml
- The Next Web: https://www.thenextweb.com/feed/
- TechRadar: https://www.techradar.com/feeds/articletype/news
- Gizmodo: https://www.gizmodo.com/feed/rss
- Slashdot: https://slashdot.org/rss/slashdot.rss
- The Register: https://www.theregister.com/headlines.atom
- Hacker News: https://news.ycombinator.com/rss
- Phoronix: https://www.phoronix.com/rss.php
- NetworkWorld: https://www.networkworld.com/feed/
- InfoWorld: https://www.infoworld.com/feed/
- Computerworld: https://www.computerworld.com/feed/

**LIST OF CATALAN SOURCES**
- Ara.cat: https://www.ara.cat/rss/
- VilaWeb: https://www.vilaweb.cat/feed/
- La Vanguardia: https://www.lavanguardia.com/rss/home.xml
- NacióDigital: https://naciodigital.cat/rss/
- 324.cat: https://www.324.cat/rss
- Softcatalà: https://www.softcatala.org/feed/
- El Nacional.cat: https://www.elnacional.cat/?feed=rss2
- El Mon.cat: https://www.elmon.cat/feed/
- Betevé: https://www.beteve.cat/feed/
- RAC1: https://www.rac1.cat/?feed=rss2
- El Punt Avui: https://www.elpuntavui.cat/feed/
- Segre: https://www.segre.com/?feed=rss2
- Regio7: https://www.regio7.cat/?feed=rss2
- Diari de Balears: https://www.diaridebalears.cat/?feed=rss2
- Diari de Andorra: https://www.diariandorra.ad/?feed=rss2
- Nuvol: https://www.nuvol.com/feed
- Diari Mes (Tarragona): https://www.diarimes.com/?feed=rss2
- Directe.cat: https://www.directe.cat/?feed=rss2
- Cugat.cat: https://www.cugat.cat/feed/
- CatalunyaPress: https://www.catalunyapress.cat/?feed=rss2
- Tot Barcelona: https://www.totbarcelona.cat/feed/
- e-notícies: https://www.e-noticies.cat/?feed=rss2
- Lleida Diari: https://www.lleidadiari.cat/feed/
- Catorze: https://www.catorze.cat/?feed=rss2
- Xarxanet: https://www.xarxanet.org/?feed=rss2
- Bondia: https://www.bondia.cat/?feed=rss2

