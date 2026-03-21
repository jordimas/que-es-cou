Your task is to classify articles from the raw feeds and output a list of article link_ids that pass the tech topic filter.

**INPUT DATA**

Read the following files:
- output/raw_feeds_world.json
- output/raw_feeds_catalunya.json

Do not fetch any URLs yourself. Use only the data in these files.

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

**TASK**

Classify all articles in raw_feeds_world.json and raw_feeds_catalunya.json using the tech topic filter.

Output a JSON object with passing link_ids grouped by category.

**RULES FOR THE JSON**
- Output nothing except the JSON object — no markdown, no code fences, no explanation, no HTML, no trailing text
- Filename is output/tech_topic_filter_new.json
- The JSON must strictly follow this schema:

{
  "world": ["link_id_1", "link_id_2", ...],
  "catalunya": ["link_id_1", "link_id_2", ...]
}
