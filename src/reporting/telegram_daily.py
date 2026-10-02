"""Compatibility entry point for the locked daily-v1 Telegram presentation."""
from src.reporting.daily_template import render_daily_telegram


def format_daily_telegram(report, depot, report_date, drive_link='', cached=False):
    return render_daily_telegram(report, depot, report_date, drive_link, cached)
