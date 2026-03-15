#!/usr/bin/env python3
"""
render_news.py  –  Renders a news JSON file to HTML using a Jinja2 template.

Usage:
    python render_news.py                        # news.json → news.html
    python render_news.py input.json output.html # custom paths

The Jinja2 template is expected at: templates/page.html
(relative to this script, or override with --template)
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader, select_autoescape

# ── CLI args ───────────────────────────────────────────────────────────────────
input_path    = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("news.json")
output_path   = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("news.html")
template_dir  = Path(__file__).parent
template_name = "page.html"

# ── Constants ──────────────────────────────────────────────────────────────────
MONTHS_CA = {
    "01": "gener",    "02": "febrer",   "03": "març",     "04": "abril",
    "05": "maig",     "06": "juny",     "07": "juliol",   "08": "agost",
    "09": "setembre", "10": "octubre",  "11": "novembre", "12": "desembre",
}

TAB_TITLES = {
    "world":     "Al món",
    "catalunya": "Països Catalans",
    "podcasts":  "Podcasts",
}


# ── Data helpers ───────────────────────────────────────────────────────────────
def format_date_ca(iso: str) -> str:
    """'2026-03-14' or '2026-03-14T19:36' → '14 de març de 2026'"""
    try:
        date_part = iso.split("T")[0]
        y, m, d = date_part.split("-")
        return f"{int(d)} de {MONTHS_CA[m]} de {y}"
    except Exception:
        return iso


def source_domain(url: str) -> str:
    """Extract scheme+host from a URL, fallback to '#'."""
    try:
        p = urlparse(url)
        return f"{p.scheme}://{p.netloc}"
    except Exception:
        return "#"


def prepare_sections(raw_sections: list) -> list:
    """Enrich section and article dicts with display-ready fields."""
    sections = []
    for sec in raw_sections:
        articles = []
        for art in sec.get("articles", []):
            articles.append({
                **art,
                "date_display": format_date_ca(art.get("date", "")),
            })
        enriched = {
            **sec,
            "tab_title": TAB_TITLES.get(sec.get("id", ""), sec.get("title", "")),
            "articles":  articles,
        }
        enriched["sources"] = collect_sources_for_section(enriched)
        sections.append(enriched)
    return sections


def collect_sources_for_section(section: dict) -> list:
    """Return deduplicated list of {name, url} dicts for a single section's articles."""
    seen, sources = set(), []
    for art in section.get("articles", []):
        name = art.get("source", "").strip()
        if name and name not in seen:
            seen.add(name)
            sources.append({"name": name, "url": source_domain(art.get("url", ""))})
    return sources


# ── Load JSON ──────────────────────────────────────────────────────────────────
try:
    data = json.loads(input_path.read_text(encoding="utf-8"))
except FileNotFoundError:
    sys.exit(f"Error: '{input_path}' not found.")
except json.JSONDecodeError as e:
    sys.exit(f"Error: invalid JSON in '{input_path}': {e}")

# ── Build template context ─────────────────────────────────────────────────────
generated_at = data.get("generated_at", datetime.today().strftime("%Y-%m-%d"))
generated_time = generated_at[11:16] if len(generated_at) > 10 else ""

context = {
    "generated_at": generated_at,
    "date_display": format_date_ca(generated_at),
    "generated_time": generated_time,
    "sections":     prepare_sections(data.get("sections", [])),
}

# ── Render ─────────────────────────────────────────────────────────────────────
env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=select_autoescape(["html"]),
)
template = env.get_template(template_name)
html = template.render(**context)

output_path.write_text(html, encoding="utf-8")
print(f"✅  HTML written to '{output_path}'")
