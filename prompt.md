Your task is to execute the following instructions:

**FETCHING CRITERIA**

- What to fetch
  - Check all news sources for tech stories published in the last 48 hours
  - For world news, fetch 50 articles across at least 30 technology sources
    - Use these exact RSS URLs in the LIST OF WORLD SOURCES section
  - For Catalan news, fetch 50 articles across at least 20 sources
    - Include all the sources that you are aware of in Catalan language
    - Make sure to include the following, using LIST OF CATALAN SOURCES section:
  - For podcasts, fetch the RSS feeds of Catalan technology podcasts
    - Use these exact RSS URLs in the LIST OF PODCAST SOURCES section
    - Include only episodes published in the last hour
- How
  - When fetching websites, use a standard Mozilla user agent (not Claude's), with curl if needed
  - If a source is blocked or returns an error, skip it and try the next one
  - Keep track of every source URL you attempt to fetch, and record whether it succeeded or failed
- Permissions
  - Do not ask permission to run any CLI tool
  - Allow fetching any external web content

**SELECTION CRITERIA**
- News have to be published in the last 48 hours
- News must be about technology
- Select up to the top 10 most important world news related to technology
 - Important criteria: voted, cited, or popular across different media
- Select up to the top 10 most important Catalan/local news about technology
 - Important criteria: voted, cited, or popular across different media
 - It is OK if we cannot get 10 articles, it is more important that meet the criteria
- For podcasts: include all episodes published in the last hour from the LIST OF PODCAST SOURCES
 - Do not filter by topic; include any episode published in the last hour
 - If no episodes were published in the last hour, the articles array must be empty
- For videos: include videos published in the last 48 hours from the LIST OF VIDEO SOURCES
 - Do not filter by topic; include any video published in the last 48 hours
 - If no videos were published in the last 48 hours, the articles array must be empty
- For events: fetch upcoming technology events in Catalonia from the LIST OF EVENT SOURCES
 - Include events happening in the next 30 days
 - If no upcoming events are found, the articles array must be empty
 
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
    },
    {
      "id": "podcasts",
      "title": "Podcasts en català sobre tecnologia",
      "sources_checked": [
        {
          "name": "Podcast name",
          "url": "https://...",
          "status": "ok | blocked | error",
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
      "id": "videos",
      "title": "Vídeos en català sobre tecnologia",
      "sources_checked": [
        {
          "name": "Channel name",
          "url": "https://...",
          "status": "ok | blocked | error",
          "articles_found": 0
        }
      ],
      "articles": [
        {
          "title": "Video title",
          "url": "https://...",
          "source": "Channel name",
          "date": "YYYY-MM-DD",
          "time": "HH:MM",
          "summary": "Summary in Catalan, maximum 20 words."
        }
      ]
    },
    {
      "id": "events",
      "title": "Esdeveniments tecnològics a Catalunya",
      "sources_checked": [
        {
          "name": "Source name",
          "url": "https://...",
          "status": "ok | blocked | error",
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
- Diari d'Andorra: https://www.diariandorra.ad/?feed=rss2
- RTVA (Ràdio i Televisió d'Andorra): https://www.rtva.ad/feed/
- Bon Dia Andorra: https://www.bondia.ad/?feed=rss2
- Altaveu: https://www.altaveu.com/?feed=rss2
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
- El Temps: https://www.eltemps.cat/feed/
- Àpunt: https://www.apunt.media/feed/
- Nació Valenciana: https://naciovalenciana.cat/feed/
- El Periòdic d'Ontinyent: https://www.elperiodicvalencia.com/?feed=rss2
- Saó: https://www.saodijous.com/?feed=rss2
- Diari de Balears: https://www.diaridebalears.cat/?feed=rss2
- IB3 Notícies: https://ib3.org/feed/
- Ara Balears: https://www.arabalears.cat/rss/
- Coanegra: https://coanegra.cat/?feed=rss2
- Manacor Comarcal: https://manacorcomarcal.com/?feed=rss2
- L'Independant (Catalunya Nord): https://www.lindependant.fr/arc/outboundfeeds/rss/
- El Pou de la Gallina: https://elpoudegallina.com/?feed=rss2
- Nacionalcatalà (Catalunya Nord): https://www.nacionalcatala.com/?feed=rss2

**LIST OF VIDEO SOURCES**
- Softcatalà (YouTube): https://www.youtube.com/feeds/videos.xml?channel_id=UCpZoAe9KsxE5bZVB1G1VTJA
- VilaWeb (YouTube): https://www.youtube.com/feeds/videos.xml?channel_id=UCi3p6kbLHy7a1EcLNmqwFuA
- Betevé (YouTube): https://www.youtube.com/feeds/videos.xml?channel_id=UC2RL-t1_-TEFhxQE-4A0zHw
- 3Cat (YouTube): https://www.youtube.com/feeds/videos.xml?channel_id=UCQAQnGFUBYVaFhJhGrfY6vg
- Escola d'Enginyeria UAB (YouTube): https://www.youtube.com/feeds/videos.xml?channel_id=UCwVEPCFI93-D6SIyvb_wbpA
- IB3 (YouTube): https://www.youtube.com/feeds/videos.xml?channel_id=UCh5NJ5Wx2SbDQ7oZcJz9-Ig

**LIST OF EVENT SOURCES**
- Meetup Barcelona Tech: https://www.meetup.com/find/?location=Barcelona&source=EVENTS&categoryId=546&type=upcoming
- BcnEng (Meetup): https://www.meetup.com/bcneng/events/rss/
- Startup Grind Barcelona: https://www.meetup.com/startup-grind-barcelona/events/rss/
- Tech Barcelona: https://techbarcelona.com/events/
- Mobile World Congress: https://www.mwcbarcelona.com/agenda/rss
- 4YFN: https://www.4yfn.com/agenda/
- IOC Tech Events: https://lanyrd.com/places/barcelona/tech/

**LIST OF PODCAST SOURCES**
- La Base: https://rss.ivoox.com/podcast/la-base_sq_f1712297_1.xml
- Bits de Ciència: https://feeds.soundcloud.com/users/soundcloud:users:302945232/sounds.rss
- La Tecnologia al Dia (Catalunya Ràdio): https://rss.audioboom.com/channels/5025358.rss
- Crims de la xarxa (iVoox): https://rss.ivoox.com/podcast/crims-de-la-xarxa_sq_f12305773_1.xml
- Dades obertes (Catalunya Ràdio): https://api.3cat.cat/audio/podcasts?_format=rss&id=117&version=2.0
- El Terrat de la tecnologia: https://rss.ivoox.com/podcast/terrat-tecnologia_sq_f1700107_1.xml
- Mossegar la poma: https://rss.ivoox.com/podcast/mossegar-poma_sq_f1139235_1.xml
- Tecnicat (podcast): https://rss.ivoox.com/podcast/tecnicat_sq_f12054621_1.xml
