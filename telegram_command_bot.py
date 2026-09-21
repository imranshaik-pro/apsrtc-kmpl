"""Telegram command processor for APSRTC automation.

Designed for a single authorized Telegram chat.  GitHub Actions supplies the
bot token, authorized chat id, and a repository token; no secrets are stored
in source.
"""
from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta


API = "https://api.telegram.org/bot{token}/{method}"
REPO = os.getenv("GITHUB_REPOSITORY", "imranshaik-pro/apsrtc-kmpl")
REF = os.getenv("GITHUB_REF_NAME", "master")


def _request(url: str, *, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.load(response)


def telegram(token: str, method: str, params: dict):
    data = urllib.parse.urlencode(params).encode()
    return _request(API.format(token=token, method=method), data=data)


def send(token: str, chat_id: str, text: str):
    telegram(token, "sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": "true",
    })


def dispatch(workflow: str, inputs: dict):
    token = os.environ["GH_DISPATCH_TOKEN"].strip()
    url = f"https://api.github.com/repos/{REPO}/actions/workflows/{workflow}/dispatches"
    body = json.dumps({"ref": REF, "inputs": inputs}).encode()
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=25) as response:
        if response.status != 204:
            raise RuntimeError(f"GitHub dispatch returned HTTP {response.status}")


def normalize_vehicle(value: str) -> str:
    vehicle = re.sub(r"\s+", "", value or "").upper()
    return vehicle[2:] if vehicle.startswith("AP") else vehicle


def parse_date(value: str) -> str:
    datetime.strptime(value, "%Y-%m-%d")
    return value


def parse_month(value: str) -> str:
    datetime.strptime(value, "%Y-%m")
    return value


def help_text() -> str:
    return (
        "🚌 APSRTC PRODDUTUR BOT\n\n"
        "/daily - generate the normal Daily report\n"
        "/daily YYYY-MM-DD - Daily report for a date\n"
        "/monthly YYYY-MM - generate/refresh Monthly report\n"
        "/vehicle VEHICLE_NO - vehicle lookup (next phase)\n"
        "/status - bot/automation status\n"
        "/help - show commands\n\n"
        "Vehicle Event guided entry will be enabled after the read/report commands are validated."
    )


def handle(token: str, chat_id: str, text: str):
    parts = text.strip().split()
    command = parts[0].split("@", 1)[0].lower() if parts else ""

    if command in ("/start", "/help"):
        send(token, chat_id, help_text())
        return

    if command == "/status":
        send(token, chat_id, "✅ APSRTC automation bot is online.\nAuthorized chat verified.\nRepository: " + REPO)
        return

    if command == "/daily":
        if len(parts) not in (2, 3):
            send(token, chat_id, "Usage: /daily DEPOT or /daily DEPOT YYYY-MM-DD")
            return
        depot = parts[1].strip().upper()
        report_date = ""
        if len(parts) == 3:
            try:
                report_date = parse_date(parts[2])
            except ValueError:
                send(token, chat_id, "Invalid date. Use YYYY-MM-DD.")
                return
            if date.fromisoformat(report_date) > date.today():
                send(token, chat_id, "Future Daily report dates are not allowed.")
                return
        dispatch("daily-report.yml", {"depot": depot, "report_date": report_date})
        send(token, chat_id, f"⏳ Daily report requested for {depot}" + (f" on {report_date}" if report_date else "") + ".\\nThe existing Daily workflow will deliver the report here when complete.")
        return

    if command == "/monthly":
        if len(parts) != 3:
            send(token, chat_id, "Usage: /monthly DEPOT YYYY-MM")
            return
        depot = parts[1].strip().upper()
        try:
            month = parse_month(parts[2])
        except ValueError:
            send(token, chat_id, "Invalid month. Use YYYY-MM.")
            return
        if month > date.today().strftime("%Y-%m"):
            send(token, chat_id, "Future Monthly report months are not allowed.")
            return
        dispatch("monthly-report.yml", {"depot": depot, "month": month})
        send(token, chat_id, f"⏳ Monthly report requested for {depot} — {month}.")
        return

    if command == "/vehicle":
        if len(parts) != 2:
            send(token, chat_id, "Usage: /vehicle VEHICLE_NO")
            return
        vehicle = normalize_vehicle(parts[1])
        if not vehicle:
            send(token, chat_id, "Vehicle number is required.")
            return
        send(token, chat_id, f"ℹ️ Vehicle lookup for {vehicle} is reserved for the next phase; no report was triggered.")
        return

    send(token, chat_id, "Unknown command. Send /help to see available commands.")


def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"].strip()
    authorized = os.environ["TELEGRAM_CHAT_ID"].strip()
    offset = int(os.getenv("TELEGRAM_OFFSET", "0") or 0)
    payload = telegram(token, "getUpdates", {
        "offset": offset,
        "timeout": 0,
        "allowed_updates": json.dumps(["message"]),
    })
    updates = payload.get("result", [])
    max_update = offset
    for update in updates:
        update_id = int(update.get("update_id", 0))
        max_update = max(max_update, update_id + 1)
        message = update.get("message") or {}
        incoming_chat = str((message.get("chat") or {}).get("id", ""))
        text = str(message.get("text") or "").strip()
        if incoming_chat != authorized:
            if incoming_chat:
                send(token, incoming_chat, "Unauthorized chat.")
            continue
        if text.startswith("/"):
            handle(token, authorized, text)
    print(f"TELEGRAM_COMMANDS_OK: {len(updates)} update(s); next_offset={max_update}")


if __name__ == "__main__":
    main()
