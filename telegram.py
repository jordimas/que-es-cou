#!/usr/bin/env python3

"""
tg-post.py — CLI tool to post HTML messages to a Telegram channel

Usage:
  python tg-post.py --message "<b>Hello</b> World"
  python tg-post.py --file ./post.html
  echo "<b>Hello</b>" | python tg-post.py

Config via environment variables (or a .env file):
  TG_TOKEN   — your Telegram bot token
  TG_CHAT_ID — your channel ID (e.g. -1001234567890)
"""

import argparse
import json
import os
import select
import sys
import urllib.error
import urllib.request
from pathlib import Path


# ─── Load .env if present ─────────────────────────────────────────────────────
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


# ─── Read HTML from stdin (non-blocking) ─────────────────────────────────────
def read_stdin():
    if sys.stdin.isatty():
        return None
    return sys.stdin.read().strip() or None


# ─── Convert full HTML doc → Telegram-safe HTML ──────────────────────────────
def html_to_telegram(raw: str) -> str:
    """
    Extracts content from a full HTML document and converts it to
    Telegram-compatible HTML (only b, i, u, s, code, pre, a are supported).
    Uses only stdlib — no pip required.
    """
    import re
    from html.parser import HTMLParser

    SUPPORTED = {"b", "strong", "i", "em", "u", "s", "del", "code", "pre", "a"}
    REMAP = {"strong": "b", "em": "i", "del": "s"}
    BLOCK_TAGS = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6",
                  "li", "tr", "br", "hr", "section", "article"}
    SKIP_TAGS = {"script", "style", "head", "noscript", "svg"}
    VOID_TAGS = {"meta", "link", "br", "hr", "img", "input", "area",
                 "base", "col", "embed", "param", "source", "track", "wbr"}

    class TelegramHTMLParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.result = []
            self.skip_depth = 0
            self.in_body = False

        def handle_starttag(self, tag, attrs):
            if tag == "body":
                self.in_body = True
                return
            if tag in VOID_TAGS:
                return
            if self.skip_depth > 0:
                self.skip_depth += 1
                return
            if tag in SKIP_TAGS:
                self.skip_depth += 1
                return
            if not self.in_body:
                return
            tag_out = REMAP.get(tag, tag)
            if tag_out in SUPPORTED:
                if tag_out == "a":
                    href = dict(attrs).get("href", "")
                    self.result.append(f'<a href="{href}">')
                else:
                    self.result.append(f"<{tag_out}>")
            elif tag in BLOCK_TAGS:
                if self.result and not self.result[-1].endswith("\n"):
                    self.result.append("\n")

        def handle_endtag(self, tag):
            if tag == "body":
                return
            if tag in VOID_TAGS:
                return
            if self.skip_depth > 0:
                self.skip_depth -= 1
                return
            if not self.in_body:
                return
            tag_out = REMAP.get(tag, tag)
            if tag_out in SUPPORTED:
                self.result.append(f"</{tag_out}>")
            elif tag in BLOCK_TAGS:
                self.result.append("\n")

        def handle_data(self, data):
            if self.skip_depth > 0 or not self.in_body:
                return
            self.result.append(data)

        def get_output(self):
            text = "".join(self.result)
            text = re.sub(r"\n{3,}", "\n\n", text)
            return text.strip()

    p = TelegramHTMLParser()
    if "<body" not in raw.lower():
        raw = f"<body>{raw}</body>"
    p.feed(raw)
    return p.get_output()


# ─── Split HTML into safe chunks (max 4096 chars) ────────────────────────────
def split_html(html: str, limit: int = 4096) -> list[str]:
    """
    Splits HTML into chunks that fit within Telegram's limit.
    Tries to break on paragraph/line boundaries to avoid cutting mid-tag.
    """
    if len(html) <= limit:
        return [html]

    chunks = []
    while html:
        if len(html) <= limit:
            chunks.append(html)
            break

        # Try to find a clean break point within the limit (paragraph, newline)
        chunk = html[:limit]
        break_pos = max(
            chunk.rfind("\n\n"),
            chunk.rfind("</p>"),
            chunk.rfind("</li>"),
            chunk.rfind("\n"),
        )

        if break_pos <= 0:
            # No clean break found — hard cut at limit
            break_pos = limit

        chunks.append(html[:break_pos].strip())
        html = html[break_pos:].strip()

    return [c for c in chunks if c]


# ─── Send to Telegram ─────────────────────────────────────────────────────────
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


# ─── CLI argument parser ──────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tg-post",
        description="Post HTML messages to a Telegram channel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python tg-post.py --message "<b>Breaking News</b>: Something happened"
  python tg-post.py --file ./post.html
  python tg-post.py --message "<i>Test</i>" --silent
  echo "<b>Hello</b>" | python tg-post.py

environment variables:
  TG_TOKEN      Your Telegram bot token
  TG_CHAT_ID    Your channel ID (e.g. -1001234567890)
        """,
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("-m", "--message", metavar="HTML", help="HTML string to send")
    source.add_argument("-f", "--file", metavar="PATH", help="Path to an HTML file to send")

    parser.add_argument("-t", "--token", metavar="TOKEN", help="Telegram bot token (overrides TG_TOKEN)")
    parser.add_argument("-c", "--chat", metavar="ID", help="Channel chat ID (overrides TG_CHAT_ID)")
    parser.add_argument("-s", "--silent", action="store_true", help="Send without notifying subscribers")
    parser.add_argument("--preview", action="store_true", help="Print the message without sending")

    return parser


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    load_env()
    parser = build_parser()
    args = parser.parse_args()

    # ── Resolve HTML content (priority: --message > --file > stdin) ──
    html = None

    if args.message:
        html = args.message

    elif args.file:
        file_path = Path(args.file).resolve()
        if not file_path.exists():
            print(f"❌  File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        html = file_path.read_text(encoding="utf-8").strip()

    else:
        html = read_stdin()

    if not html:
        print("❌  No message provided. Use --message, --file, or pipe HTML via stdin.", file=sys.stderr)
        print("    Run with --help for usage info.", file=sys.stderr)
        sys.exit(1)

    # ── Convert full HTML doc to Telegram-safe HTML ───────────────────
    original_len = len(html)
    html = html_to_telegram(html)
    if len(html) < original_len:
        print(f"🧹  Converted to Telegram HTML ({original_len} → {len(html)} chars)")

    # ── Preview mode ──────────────────────────────────────────────────
    if args.preview:
        print("\n── Preview ──────────────────────────────────")
        print(html)
        print("─────────────────────────────────────────────\n")
        sys.exit(0)

    # ── Resolve credentials ───────────────────────────────────────────
    token = args.token or os.environ.get("TG_TOKEN")
    chat_id = args.chat or os.environ.get("TG_CHAT_ID")

    if not token:
        print("❌  Missing bot token. Set TG_TOKEN in .env or use --token.", file=sys.stderr)
        sys.exit(1)

    if not chat_id:
        print("❌  Missing chat ID. Set TG_CHAT_ID in .env or use --chat.", file=sys.stderr)
        sys.exit(1)

    # ── Split if needed ───────────────────────────────────────────────
    chunks = split_html(html)
    total = len(chunks)

    if total > 1:
        print(f"✂️   Message too long ({len(html)} chars) — splitting into {total} parts...")

    # ── Send ──────────────────────────────────────────────────────────
    print(f"📤  Sending to channel {chat_id}...")

    try:
        for i, chunk in enumerate(chunks, 1):
            if total > 1:
                print(f"   Part {i}/{total} ({len(chunk)} chars)...")

            result = send_message(token, chat_id, chunk, args.silent)

            if result.get("ok"):
                msg_id = result["result"]["message_id"]
                print(f"✅  Posted! Message ID: {msg_id}" if total == 1 else f"   ✅  Part {i} posted (ID: {msg_id})")
            else:
                print(f"❌  Telegram error: {result.get('description', 'Unknown error')}", file=sys.stderr)
                sys.exit(1)

        if total > 1:
            print(f"🎉  All {total} parts sent successfully!")

    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode("utf-8"))
        print(f"❌  HTTP {e.code}: {body.get('description', str(e))}", file=sys.stderr)
        sys.exit(1)

    except urllib.error.URLError as e:
        print(f"❌  Request failed: {e.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
