# Telegram listener deployment and usage

The scheduled GitHub workflow checks once and exits. GitHub schedules can be
delayed, so this is a fallback, not an interactive hosting service.
`telegram_listener.py` continuously long-polls Telegram on a Linux machine.
Report generation stays in the existing GitHub workflows. No public port,
webhook URL, APSRTC login or Google credentials are needed on the listener.

## Install on a machine that stays online

Requires Linux with systemd and Python 3.11+. Put this repository at
`/opt/apsrtc-kmpl`, readable by the service. No pip packages are required for
the listener. Copy `deploy/telegram.env.example` to `/etc/apsrtc-telegram.env`.
Set its permissions to 600, owned by root, and populate the configuration locally.
Never put secrets in Git or chat.

- TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID: the existing bot and authorized chat.
- GH_DISPATCH_TOKEN: a fine-grained GitHub token scoped to this repository with
  Actions write permission. A GitHub job's temporary token cannot be reused here.
- DEPOT_MASTER: the same pipe-separated depot names as the GitHub variable.
- VEHICLE_EVENTS_API_URL and VEHICLE_EVENTS_API_KEY: existing event API settings.

Before starting, set the repository Actions variable TELEGRAM_LISTENER_MODE to
`service` and let any running Telegram Command Bot job finish. This disables
scheduled polling via its job condition. Never run both consumers together.
Existing daily/monthly/annual report schedules are unaffected.

Install and start:

```bash
sudo install -m 644 /opt/apsrtc-kmpl/deploy/apsrtc-telegram.service /etc/systemd/system/apsrtc-telegram.service
sudo systemctl daemon-reload
sudo systemctl enable --now apsrtc-telegram
sudo journalctl -u apsrtc-telegram -n 30 --no-pager
```

Wait for TELEGRAM_LISTENER_READY, then send `/menu` from the authorized chat.
Choose a depot, check the options, and request one real report. Verify its GitHub
run and delivered report. Enter a real event only when ready to save it; verify
the returned event ID. Command registration alone does not validate delivery.

The service refuses to start if a webhook is already active, required settings
are absent, another local listener holds the lock, or its state belongs to a
different bot. Persistent state lives in `/var/lib/apsrtc-telegram`.
It claims each Telegram update before dispatching it. If the connection fails
during dispatch, that request is not automatically replayed: check Actions/event
records before resubmitting. This prevents automatic duplicate side effects but
does not guarantee every request completes after a crash. Check logs for
`TELEGRAM_UPDATE_FAILED` or rows left as `claimed` after a restart.

Rollback: stop the service first, then remove TELEGRAM_LISTENER_MODE or set it
to `schedule`. Run Telegram Command Bot manually if an immediate fallback check
is needed. Delayed scheduled responses will return in this mode.

## User commands

`/start` or `/menu`: depot buttons, then action buttons.

| Action | Options |
| --- | --- |
| Daily | Depot, then one of the last seven completed dates (IST) |
| Monthly | Depot, then one of six recent months |
| Annual KPI | Depot, then one of six recent reporting months |
| Vehicle Event | Depot, vehicle number, event type, one of seven recent dates, prompted details, CONFIRM or CANCEL |
| Vehicle 360 | Not yet implemented as a standalone lookup |

`/daily`, `/monthly`, `/annual`, and `/event` are shortcuts that start with
depot selection. `/status` checks that the processor responds; it does not certify
that report generation or the event API is healthy. `/help` opens instructions.

Selections show depot and the relevant date/month. Report generation takes time
after acknowledgment; the existing workflows deliver results separately.

References: https://core.telegram.org/bots/api#getupdates and
https://docs.github.com/en/actions/how-tos/troubleshoot-workflows
