Your task is to execute the following instructions:

**FETCHING CRITERIA**

- What to fetch
  - For world news, fetch 50 articles across at least 30 technology sources, prioritizing diversity across sources whenever possible.
    - Use these exact RSS URLs in the LIST OF WORLD SOURCES section
  - For Catalan news, fetch 50 articles across at least 20 sources, prioritizing diversity across sources whenever possible.
    - Include all the sources that you are aware of in Catalan language
    - Make sure to include the following, using LIST OF CATALAN SOURCES section:
  - For podcasts, fetch the RSS feeds of Catalan technology podcasts
    - Use these exact RSS URLs in the LIST OF PODCAST SOURCES section
    - Include only episodes published in the last 15 days
  - For events: fetch upcoming technology events in the Catalan Countries (Catalonia, Valencia, Balearic Islands, Andorra) from the LIST OF EVENT SOURCES
   - Include events happening in the next 30 days
   - Translate event titles and summaries to Catalan if they are in another language
   - If no upcoming events are found, the articles array must be empty
- How
  - When fetching websites, use a standard Mozilla user agent (not Claude's), with curl if needed
  - If a source is blocked or returns an error, skip it and try the next one
  - Keep track of every source URL you attempt to fetch, and record whether it succeeded or failed
- Permissions
  - Do not ask permission to run any CLI tool
  - Allow fetching any external web content

**SELECTION CRITERIA**
- All the content of all the sections MUST be about technology
- Select up to the top 10 most important world news related to technology published in the last 48 hours
 - Important criteria: prioritize stories covered by multiple sources or with significant impact
 - It is mandatory that they are about technology
- Select up to the top 10 most important Catalan/local news about technology published in the last 48 hours
 - Important criteria: prioritize stories covered by multiple sources or with significant impact
 - It is OK if we cannot get 10 articles, but it is mandatory that they are about technology
 - Reject any article that is primarily about politics, sports, culture, economy, or other non-tech topics — even if it mentions technology in passing
- For podcasts: include all episodes published in the last 15 days from the LIST OF PODCAST SOURCES
 - Include any episode published in the last 15 days which is about technology
 - If no episodes were published in the last 15 days, the articles array must be empty
 - Episodes older than 15 days from today must be excluded — check the date carefully before including
 
**OUTPUT FORMAT**
- If the headlines are in Catalan, keep the original headline. Do not rewrite it
- All article titles and summaries must be written in Catalan
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
      "id": "events",
      "title": "Trobades",
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


**LIST OF EVENT SOURCES**
- WordPress BCN (Meetup RSS): https://www.meetup.com/WordPressBCN/events/rss/
- Startup Grind Barcelona (Meetup RSS): https://www.meetup.com/startup-grind-barcelona/events/rss/
- BarcelonaJS (Meetup RSS): https://www.meetup.com/BarcelonaJS/events/rss/
- GDG Barcelona (Meetup RSS): https://www.meetup.com/GDG-Barcelona/events/rss/
- Agile Barcelona (Meetup RSS): https://www.meetup.com/Agile-Barcelona/events/rss/
- Docker Barcelona (Meetup RSS): https://www.meetup.com/docker-barcelona-spain/events/rss/
- Tech Barcelona (web, JSON-LD): https://www.techbarcelona.com/agenda/
- Eventbrite Barcelona Tech (web, JSON-LD): https://www.eventbrite.es/d/spain--barcelona/technology--events/

**LIST OF PODCAST SOURCES**
- La Base: https://rss.ivoox.com/podcast/la-base_sq_f1712297_1.xml
- Bits de Ciència: https://feeds.soundcloud.com/users/soundcloud:users:302945232/sounds.rss
- La Tecnologia al Dia (Catalunya Ràdio): https://rss.audioboom.com/channels/5025358.rss
- Crims de la xarxa (iVoox): https://rss.ivoox.com/podcast/crims-de-la-xarxa_sq_f12305773_1.xml
- Dades obertes (Catalunya Ràdio): https://api.3cat.cat/audio/podcasts?_format=rss&id=117&version=2.0
- El Terrat de la tecnologia: https://rss.ivoox.com/podcast/terrat-tecnologia_sq_f1700107_1.xml
- Mossegar la poma: https://podcasts.cat/32/index.xml
- Tecnicat (podcast): https://rss.ivoox.com/podcast/tecnicat_sq_f12054621_1.xml
- Revolució 4.0: https://podcasts.cat/143/index.xml
- L'altra ràdio: https://podcasts.cat/36/index.xml
- El Gòtic: https://podcasts.cat/191/index.xml
- Generació digital: https://podcasts.cat/28/index.xml
- Societat de la Informació: https://podcasts.cat/54/index.xml
- Internet amb Genís Roca: https://podcasts.cat/247/index.xml
- La poma de Newton: https://podcasts.cat/40/index.xml
- Perspectiva: https://podcasts.cat/178/index.xml
- Ciència al Versió RAC1: https://podcasts.cat/162/index.xml
