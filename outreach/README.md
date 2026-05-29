# Eretz Realty — Automated Outreach Program

A self-contained outreach automation that runs **inside your own Google account**
via Google Apps Script. No external service, no recurring cost, full send rights.

It does two jobs:

1. **Scheduled sending** (`sendBatch`) — emails recipients from a Google Sheet
   automatically, throttled (default 12/day, Tue–Thu, spaced 45s apart), with
   duplicate protection and per-row status tracking.
2. **Reply monitoring + reporting** (`checkRepliesAndReport`) — every 10 minutes
   during business hours, scans Gmail for replies from your prospects and emails
   a report to **yitzi@eretzltd.com** (prospect name, company, email, original
   subject, reply time, short summary). **Never sends follow-ups automatically.**

## Files
- `Code.gs` — the full Apps Script (paste into script.google.com).
- `recipients.csv` — your 49 prospects (To, Name, Kind, Subject, Body + tracking cols).

## Setup (one time, ~5 minutes)

1. **Create the sheet.** New Google Sheet → File → Import → upload `recipients.csv`
   → "Replace current sheet". Rename the tab to **`Outreach`**.
2. **Open the script editor.** In the sheet: Extensions → Apps Script.
3. **Paste the code.** Delete the default `Code.gs` contents, paste in this `Code.gs`, Save.
4. **Configure.** Edit the `CONFIG` block at the top:
   - `FROM_ALIAS` — leave `''` for your default address, or put `'yitzi@eretzltd.com'`
     if you've added it as a verified send-as alias in Gmail settings.
   - `DAILY_LIMIT`, `SEND_HOUR`, `SEND_DAYS`, `MIN_GAP_SEC` — pace of sending.
   - `REPORT_TO` — already set to yitzi@eretzltd.com.
   - Keep `DRY_RUN: true` for the first run to preview safely.
5. **Test safely.**
   - Run `sendTestToSelf` → grant permissions when prompted → confirm you get the test.
   - Run `sendBatch` once with `DRY_RUN: true`; open View → Logs to see what *would* send.
6. **Go live.** Set `DRY_RUN: false`. Then run **once each**:
   - `setupTriggers()` → installs the daily auto-sender.
   - `setupReplyMonitor()` → installs the every-10-min reply watcher.

That's it. Google now runs both on schedule; you never click send.

## Controls
- Pause sending: run `removeTriggers()`. Pause reply alerts: `removeReplyMonitor()`.
- Stop a single recipient: put `SKIP` in their **Status** cell.
- Delay a recipient: put a future date in their **ScheduledFor** cell.
- Re-send to someone: clear their **Status** cell.

## Deliverability notes
Gmail is not a bulk-mail platform (≈500 sends/day hard cap, and aggressive
identical sending risks spam-foldering or account flags). The defaults are
deliberately conservative. Keep volume modest and the messages slightly varied.

## Status columns the script writes
- **Status**: `SENT`, `SKIP`, or `ERROR`
- **SentAt**: timestamp sent, or the dedup/error reason
