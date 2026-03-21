#!/usr/bin/env python3

"""
telegram.py — Post filtered news to a Telegram channel with deduplication.

Reads news.json + links.json, skips articles already sent (tracked in
telegram.json), builds per-section messages, sends new ones, and updates
telegram.json with the hashes of sent items.

Config via environment variables (or a .env file):
  TG_TOKEN   — your Telegram bot token
  TG_CHAT_ID — your channel ID (e.g. -1001234567890)
"""

import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

from news_utils import SECTION_LABELS, format_date_ca, load_news


# ─── Helpers ──────────────────────────────────────────────────────────────────

def load_env():
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    value = value.strip().strip("\"'")
                    os.environ.setdefault(key.strip(), value)


def item_hash(url: str, title: str) -> str:
    return hashlib.sha256(f"{url}\n{title}".encode()).hexdigest()[:16]


def load_sent_hashes(telegram_json_path: Path) -> set:
    if telegram_json_path.exists():
        try:
            data = json.loads(telegram_json_path.read_text(encoding="utf-8"))
            return set(data.get("sent", []))
        except (json.JSONDecodeError, KeyError):
            pass
    return set()


def save_sent_hashes(telegram_json_path: Path, hashes: set):
    telegram_json_path.write_text(
        json.dumps({"sent": sorted(hashes)}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# ─── Telegram API ─────────────────────────────────────────────────────────────

def send_message(token: str, chat_id: str, html: str, silent: bool = False) -> dict:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": html,
        "parse_mode": "HTML",
        "disable_notification": silent,
        "link_preview_options": {"is_disabled": True},
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def split_message(html: str, limit: int = 4096) -> list:
    if len(html) <= limit:
        return [html]
    chunks = []
    while html:
        if len(html) <= limit:
            chunks.append(html)
            break
        chunk = html[:limit]
        break_pos = max(
            chunk.rfind("\n\n"),
            chunk.rfind("</a>"),
            chunk.rfind("\n"),
        )
        if break_pos <= 0:
            break_pos = limit
        chunks.append(html[:break_pos].strip())
        html = html[break_pos:].strip()
    return [c for c in chunks if c]


# ─── Build message ────────────────────────────────────────────────────────────

def build_message(sections: list, date_display: str, generated_time: str,
                  sent_hashes: set) -> tuple:
    """
    Returns (message_text, new_hashes) where new_hashes are hashes of items
    included in this message.
    """
    lines = [f"<b>Què es cou</b> — {date_display} {generated_time}".strip(),
             "https://jordimas.github.io/que-es-cou/"]
    new_hashes = set()

    for sec in sections:
        articles = sec.get("articles", [])
        new_articles = [a for a in articles if item_hash(a["url"], a["title"]) not in sent_hashes]
        if not new_articles:
            continue

        label = SECTION_LABELS.get(sec.get("id", ""), sec.get("title", ""))
        lines.append("")
        lines.append(f"<b>{label}</b>")
        for art in new_articles:
            h = item_hash(art["url"], art["title"])
            new_hashes.add(h)
            source = art.get("source", "")
            date_str = format_date_ca(art["date"]) if art.get("date") else ""
            source_date = f'{source} — {date_str}' if source and date_str else source or date_str
            lines.append(f'• <a href="{art["url"]}">{art["title"]}</a>')
            if source_date:
                lines.append(f'  {source_date}')
            if art.get("summary"):
                lines.append(f'  {art["summary"]}')

    return "\n".join(lines), new_hashes


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    load_env()

    send_only = "--send-only" in sys.argv
    save_only = "--save-only" in sys.argv

    base = Path(__file__).parent / "output"
    telegram_json_path = base / "telegram.json"
    news_telegram_path = base / "news.telegram"

    # ── Send-only mode: POST news.telegram as-is, no hash management ──────────
    if send_only:
        if not news_telegram_path.exists():
            print("news.telegram not found, nothing to send.")
            return
        message = news_telegram_path.read_text(encoding="utf-8").strip()
        if not message:
            print("news.telegram is empty, nothing to send.")
            return

        token = os.environ.get("TG_TOKEN")
        chat_id = os.environ.get("TG_CHAT_ID")
        if not token:
            sys.exit("Error: missing TG_TOKEN")
        if not chat_id:
            sys.exit("Error: missing TG_CHAT_ID")

        chunks = split_message(message)
        print(f"Sending news.telegram in {len(chunks)} message(s)...")
        try:
            for i, chunk in enumerate(chunks, 1):
                result = send_message(token, chat_id, chunk)
                if result.get("ok"):
                    msg_id = result["result"]["message_id"]
                    print(f"  Part {i}/{len(chunks)} sent (ID: {msg_id})")
                else:
                    sys.exit(f"Telegram error: {result.get('description', 'Unknown error')}")
        except urllib.error.HTTPError as e:
            body = json.loads(e.read().decode("utf-8"))
            sys.exit(f"HTTP {e.code}: {body.get('description', str(e))}")
        except urllib.error.URLError as e:
            sys.exit(f"Request failed: {e.reason}")
        return

    # ── Save-only mode: update telegram.json, do not send ─────────────────────
    data, sections = load_news(Path(__file__).parent / "output")

    sent_hashes = load_sent_hashes(telegram_json_path)

    generated_at = data.get("generated_at", "")
    date_display = format_date_ca(generated_at)
    generated_time = generated_at[11:16] if len(generated_at) > 10 else ""

    message, new_hashes = build_message(sections, date_display, generated_time, sent_hashes)

    if not new_hashes:
        print("No new articles to send.")
        return

    if save_only:
        all_hashes = sent_hashes | new_hashes
        save_sent_hashes(telegram_json_path, all_hashes)
        print(f"telegram.json updated with {len(new_hashes)} new hashes ({len(all_hashes)} total), nothing sent.")
        return

    # ── Normal mode: send then save ────────────────────────────────────────────
    token = os.environ.get("TG_TOKEN")
    chat_id = os.environ.get("TG_CHAT_ID")

    if not token:
        sys.exit("Error: missing TG_TOKEN")
    if not chat_id:
        sys.exit("Error: missing TG_CHAT_ID")

    chunks = split_message(message)
    print(f"Sending {len(new_hashes)} new articles in {len(chunks)} message(s)...")

    try:
        for i, chunk in enumerate(chunks, 1):
            result = send_message(token, chat_id, chunk)
            if result.get("ok"):
                msg_id = result["result"]["message_id"]
                print(f"  Part {i}/{len(chunks)} sent (ID: {msg_id})")
            else:
                sys.exit(f"Telegram error: {result.get('description', 'Unknown error')}")
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode("utf-8"))
        sys.exit(f"HTTP {e.code}: {body.get('description', str(e))}")
    except urllib.error.URLError as e:
        sys.exit(f"Request failed: {e.reason}")

    all_hashes = sent_hashes | new_hashes
    save_sent_hashes(telegram_json_path, all_hashes)
    print(f"telegram.json updated ({len(all_hashes)} total hashes)")


if __name__ == "__main__":
    main()
