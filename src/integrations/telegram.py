#!/usr/bin/env python3
"""Telegram delivery helper for APSRTC Daily text reports.

Reads the already-generated UTF-8 report file. It does not recalculate or
rewrite report data. Delivery failure is reported to the caller.
"""
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path


def _send(text: str) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        raise RuntimeError("Telegram credentials are not configured")

    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": "true",
    }).encode()
    req = urllib.request.Request(
        "https://api.telegram.org/bot" + token + "/sendMessage",
        data=data,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        payload = json.load(response)
    if not payload.get("ok"):
        raise RuntimeError("Telegram sendMessage failed")


def send_daily_report(report_path: str, depot: str, report_date: str, drive_link: str = "") -> int:
    body = Path(report_path).read_text(encoding="utf-8", errors="replace").strip()
    header = f"🚌 APSRTC DAILY REPORT\nDepot: {depot}\nDate: {report_date}\n\n"
    footer = "\n\n✅ Uploaded to Google Drive"
    if drive_link and drive_link.startswith("http"):
        footer += "\n📄 Report: " + drive_link

    remaining = header + body + footer
    chunks = []
    while remaining:
        if len(remaining) <= 3800:
            chunks.append(remaining)
            break
        cut = remaining.rfind("\n", 0, 3800)
        if cut < 1900:
            cut = 3800
        chunks.append(remaining[:cut].rstrip())
        remaining = remaining[cut:].lstrip("\n")

    total = len(chunks)
    for index, chunk in enumerate(chunks, 1):
        prefix = f"Part {index}/{total}\n\n" if total > 1 else ""
        _send(prefix + chunk)
    return total
