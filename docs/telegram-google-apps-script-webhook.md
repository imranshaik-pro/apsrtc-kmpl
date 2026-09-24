# Telegram webhook on Google Apps Script

This is the low-resource Telegram hosting option. Telegram calls the Apps Script
web app only when a message or button press arrives. Apps Script then dispatches
the existing GitHub Actions workflows for Daily, Monthly, Annual KPI, and
Vehicle Event. Report generation stays in GitHub and Google Drive/Sheets.

No laptop, PC, or always-on VM is required after setup.

## Files

- `deploy/telegram_webhook_apps_script.gs`: Apps Script source.
- `.github/workflows/telegram-command-bot.yml`: scheduled polling fallback,
  disabled when the repository variable `TELEGRAM_LISTENER_MODE` is `webhook`.

## Required Apps Script properties

Create one Apps Script project and add these Script Properties:

| Property | Value |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | Existing Telegram bot token |
| `TELEGRAM_CHAT_ID` | Authorized Telegram chat ID |
| `GH_DISPATCH_TOKEN` | Fine-grained GitHub token with Actions write permission for this repo |
| `GITHUB_REPOSITORY` | `imranshaik-pro/apsrtc-kmpl` |
| `GITHUB_REF_NAME` | `master` |
| `DEPOT_MASTER` | Same pipe-separated depot list used by the repo variable |
| `VEHICLE_EVENTS_API_URL` | Existing Vehicle Event API URL |
| `VEHICLE_EVENTS_API_KEY` | Existing Vehicle Event API key |
| `WEBHOOK_URL` | Apps Script web app deployment URL |

The GitHub token is needed because Apps Script is outside GitHub Actions. The
temporary `${{ github.token }}` available inside workflows cannot be reused here.

## Deploy

1. Create a new Google Apps Script project.
2. Paste `deploy/telegram_webhook_apps_script.gs` into `Code.gs`.
3. Add the Script Properties listed above.
4. Deploy as Web App:
   - Execute as: Me
   - Who has access: Anyone
5. Copy the Web App URL and save it as `WEBHOOK_URL` in Script Properties.
6. Run `setupTelegramWebhook()` once from Apps Script.
7. In GitHub repository variables, set `TELEGRAM_LISTENER_MODE` to `webhook`.
8. Send `/menu` to the Telegram bot and test one report request.

If you later want to return to scheduled polling, run
`removeTelegramWebhook()` in Apps Script and clear `TELEGRAM_LISTENER_MODE` or
set it to `schedule`.

## User flow

`/menu` shows depot buttons first. After depot selection, the bot shows:

| Action | User selection |
| --- | --- |
| Daily Report | One of the last seven completed IST dates |
| Monthly Report | One of six recent months |
| Annual KPI | One of six recent reporting months |
| Vehicle Event | Vehicle number, event type, event date, details, then `CONFIRM` |
| Vehicle 360 | Shown as unavailable until that lookup is implemented |

Each report request confirms the depot and selected date/month before the
existing workflow starts. The workflow sends the final completion message and
report link when generation finishes.

## Notes

Telegram webhook and `getUpdates` polling cannot run together. Once webhook mode
is active, keep the scheduled Telegram Command Bot fallback disabled by leaving
`TELEGRAM_LISTENER_MODE=webhook`.

Apps Script stores only the current authorized chat's short event-entry state in
Script Properties while a Vehicle Event is being entered. The event is sent to
the existing API only after the user replies `CONFIRM`.
