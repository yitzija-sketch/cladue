# Eretz Realty — AI Inside-Sales Outreach Machine

A self-contained outreach + reply-handling system that runs **inside your own
Google account** via Google Apps Script. No external service, no recurring cost,
full send rights. It behaves like an inside-sales assistant working all day.

## What it does

**1. Smart scheduled sending** (`sendBatch`, every 10 min in business hours)
Before each send it searches your Gmail **three ways** — by email address, by
company domain, and by company name — then picks behaviour by rule:

| Gmail history found        | Action                                  |
|----------------------------|-----------------------------------------|
| No prior contact           | Send **COLD** approved template         |
| You emailed, no reply      | Send **FOLLOWUP** template              |
| They replied before        | Send **WARM** re-engagement             |
| Active recent thread       | **Skip** (don't blast); retry later     |
| Replied recently           | **Skip** + mark `REPLIED`               |
| Unsubscribe / not interested | **Suppress forever** (`UNSUB`)        |

Throttle: **max 2 emails per run**, spaced out, 9am–5pm Mon–Fri (all configurable).

**2. Reply monitor + alerts** (`checkRepliesAndReport`, every 10 min)
Detects replies from your prospects, labels the thread in Gmail
(**Hot Lead / Replied / No Interest**), marks the sheet so they stop receiving
mail, fires an **instant alert to yitzi@eretzltd.com for hot leads**, and queues
everything for the nightly recap. **Never sends a follow-up automatically.**

**3. Nightly digest** (`sendDailyDigest`, once a day at 6pm)
One recap email to yitzi@eretzltd.com grouped into HOT / Replied / Not interested,
each with prospect, company, email, reply time, subjects, and a short summary.

"Hot" = reply contains words like *interested, need space, call me, send options,
budget, timing, square feet, tour, pricing*. "Cold" = *not interested,
unsubscribe, remove me, stop, do not contact*. Edit the keyword lists in CONFIG.

## Files
- `Code.gs` — the full script (paste into script.google.com).
- `recipients.csv` — your 49 prospects with **To, Name, Company, Domain, Kind,
  Subject, Body** + tracking columns.

## Setup (one time — then it's all buttons)
1. New Google Sheet → File → Import → upload `recipients.csv` → "Replace current
   sheet". Rename the tab to **`Outreach`**. (Keep the header row.)
2. Extensions → Apps Script. Replace the default file with `Code.gs`. Save.
3. Back on the sheet, **reload the page**. A new **📨 Outreach** menu appears.
4. From the menu, click **⚙️ Create / reset Settings tab** — gives you a plain
   table to set pace, hours, From alias, etc. with no code.
5. Click **📧 Send me a test email** (grant permissions when asked) to confirm sending works.
6. Leave **TEST mode ON**, click **✉️ Send a batch now** and **📊 Show status**
   to preview what it would do (it sends nothing in test mode).
7. When happy: menu → **🧪 Toggle TEST mode** (turns it OFF), then **▶ Start
   automation**. Done — Google runs everything on schedule.

To pause anytime: menu → **⏸ Stop automation**.

## The 📨 Outreach menu
| Click | Does |
|-------|------|
| ▶ Start automation | Installs the schedules and goes live |
| ⏸ Stop automation | Removes all schedules |
| ✉️ Send a batch now | Runs one send cycle immediately |
| 📥 Check for replies now | Scans + reports replies now |
| 🗂 Send digest now | Sends the recap now |
| 🧪 Toggle TEST mode | Flip send-for-real on/off |
| ⚙️ Create / reset Settings tab | Builds the no-code settings table |
| 🏷 Create Gmail labels | Makes the Hot Lead / Replied / … labels |
| 📧 Send me a test email | Verifies sending |
| 📊 Show status | Counts of sent / replied / suppressed |

## Settings tab (no code)
Edit values in the **Settings** tab and they apply on the next run: `DRY_RUN`
(TEST mode), `MAX_PER_RUN`, `SEND_EVERY_MIN`, `BIZ_START_HOUR`, `BIZ_END_HOUR`,
`FROM_ALIAS`, `FROM_NAME`, `REPORT_TO`, `DIGEST_HOUR`, `RECENT_REPLY_DAYS`.
(Anything not in the tab keeps the default in `CONFIG`.)

## Day-to-day controls (in the Outreach tab)
- `SKIP` in **Status** = never email this row.
- Future date in **ScheduledFor** = hold until then.
- Clear **Status** = eligible to send again.
- **Status**/**Template**/**SentAt** are written automatically so you can track progress.

## Important limits & cautions
- **Permission:** this works because it runs as *you* in your account — that's
  what gives it send rights an assistant doesn't have.
- **Gmail is not bulk mail:** ~500 sends/day hard cap, and aggressive identical
  sending risks spam-foldering or account flags. Defaults are conservative on purpose.
- **The history check is best-effort:** Gmail search is fuzzy (esp. company-name
  matches). It errs toward *holding* when a thread looks active. Spot-check early runs.
- **No facts are invented:** templates only use the name/subject/body you supply.
  Follow-up/warm templates reference your original note rather than making claims.
