#!/usr/bin/env python3
"""
render_news.py  –  Renders a news JSON file to HTML using a Jinja2 template.

Usage:
    python render_news.py                        # news.json → news.html
    python render_news.py input.json output.html # custom paths

The Jinja2 template is expected at: page.html
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

SECTION_ICONS = {
    "world":     "🌐",
    "catalunya": "🏴",
}


# ── Data helpers ───────────────────────────────────────────────────────────────
def format_date_ca(iso: str) -> str:
    """'2026-03-14' → '14 de març de 2026'"""
    try:
        y, m, d = iso.split("-")
        return f"{int(d)} de {MONTHS_CA[m]} de {y}"
    except Exception:
        return iso


def format_date_time_ca(iso_date: str, time_str: str) -> str:
    """'2026-03-14', '09:30' → '14 de març de 2026 · 09:30'"""
    date_display = format_date_ca(iso_date)
    if time_str and time_str != "00:00":
        return f"{date_display} · {time_str}"
    return date_display


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
                "date_display": format_date_time_ca(art.get("date", ""), art.get("time", "")),
            })
        sections.append({
            **sec,
            "icon":     SECTION_ICONS.get(sec.get("id", ""), "📰"),
            "articles": articles,
        })
    return sections


def collect_sources(raw_sections: list) -> list:
    """Return deduplicated list of {name, url} dicts for the footer."""
    seen, sources = set(), []
    for sec in raw_sections:
        for art in sec.get("articles", []):
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
generated_at = data.get("generated_at", datetime.today().strftime("%Y-%m-%dT%H:%M"))

# Support both "YYYY-MM-DD" and "YYYY-MM-DDTHH:MM"
if "T" in generated_at:
    generated_date, generated_time = generated_at.split("T", 1)
else:
    generated_date, generated_time = generated_at, ""

context = {
    "generated_at":      generated_at,
    "date_display":      format_date_time_ca(generated_date, generated_time),
    "sections":          prepare_sections(data.get("sections", [])),
    "sources":           collect_sources(data.get("sections", [])),
    "generated_time":    generated_time,
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

