/**
 * Eretz Realty — Automated Outreach Program (Google Apps Script)
 * --------------------------------------------------------------
 * Runs inside your own Google account. Reads recipients from a Google Sheet
 * and sends personalized emails automatically on a schedule, throttled to
 * protect deliverability, with built-in duplicate protection and per-row
 * status tracking.
 *
 * SETUP (one time):
 *   1. Create a Google Sheet, import outreach/recipients.csv into a tab.
 *   2. Rename that tab to match SHEET_NAME below (default "Outreach").
 *   3. Tools > Apps Script -> paste this file in.
 *   4. Edit the CONFIG block below to taste.
 *   5. Run setupTriggers() once and grant permissions when prompted.
 *
 * The trigger then runs sendBatch() automatically on schedule. You never
 * click "send" yourself. Set DRY_RUN=true first to preview safely.
 */

// ============================ CONFIG ============================
const CONFIG = {
  SHEET_NAME:   'Outreach',   // tab name holding the recipients
  DAILY_LIMIT:  12,           // max emails sent per run (keep modest for deliverability)
  SEND_HOUR:    9,            // hour of day (0-23, account timezone) the daily trigger fires
  SEND_DAYS:    [2, 3, 4],    // weekdays to send on: 1=Sun .. 7=Sat. [2,3,4] = Tue/Wed/Thu
  MIN_GAP_SEC:  45,           // seconds to wait between each send (avoids a burst)
  FROM_ALIAS:   '',           // '' = default address. Or a verified send-as alias, e.g. 'yitzi@eretzltd.com'
  FROM_NAME:    'Yitzi Jachimowitz', // display name on outgoing mail
  DEDUP_SENT:   true,         // skip an address you've already emailed (scans your Sent mail)
  DRY_RUN:      false,        // true = log what WOULD send, send nothing. Flip to false to go live.

  // ---- Reply monitor / reporting ----
  REPORT_TO:    'yitzi@eretzltd.com', // where reply alerts are sent
  REPLY_CHECK_EVERY_MIN: 10,  // how often the reply watcher runs
  BIZ_START_HOUR: 8,          // only report between these hours (account timezone)
  BIZ_END_HOUR:   18,
  BIZ_DAYS:     [2, 3, 4, 5, 6], // weekdays to watch: 1=Sun..7=Sat. Mon-Fri = [2,3,4,5,6]
};
// Column layout (1-based). Must match the header row of the sheet.
const COL = { TO:1, NAME:2, KIND:3, SUBJECT:4, BODY:5, SCHEDULED:6, STATUS:7, SENT_AT:8, THREAD_ID:9 };
// ================================================================


/** Run ONCE to install the recurring daily trigger. */
function setupTriggers() {
  // Clear any existing triggers for sendBatch so we don't stack duplicates.
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'sendBatch') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('sendBatch')
    .timeBased()
    .everyDays(1)
    .atHour(CONFIG.SEND_HOUR)
    .create();
  Logger.log('Trigger installed: sendBatch() daily at %s:00.', CONFIG.SEND_HOUR);
}

/** Remove the automation entirely. */
function removeTriggers() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'sendBatch') ScriptApp.deleteTrigger(t);
  });
  Logger.log('All sendBatch triggers removed.');
}


/** Main worker — invoked by the trigger (or run manually to send a batch now). */
function sendBatch() {
  const tz   = Session.getScriptTimeZone();
  const now  = new Date();
  const dow  = parseInt(Utilities.formatDate(now, tz, 'u'), 10) % 7 + 1; // 1=Sun..7=Sat

  if (CONFIG.SEND_DAYS.indexOf(dow) === -1) {
    Logger.log('Today (day %s) is not a send day. Skipping.', dow);
    return;
  }

  const sheet = SpreadsheetApp.getActive().getSheetByName(CONFIG.SHEET_NAME);
  if (!sheet) throw new Error('Sheet tab "' + CONFIG.SHEET_NAME + '" not found.');

  const lastRow = sheet.getLastRow();
  if (lastRow < 2) { Logger.log('No data rows.'); return; }

  const data = sheet.getRange(2, 1, lastRow - 1, COL.THREAD_ID).getValues();
  let sent = 0;

  for (let i = 0; i < data.length; i++) {
    if (sent >= CONFIG.DAILY_LIMIT) break;

    const row    = i + 2;
    const to      = String(data[i][COL.TO - 1]).trim();
    const subject = String(data[i][COL.SUBJECT - 1]);
    const body    = String(data[i][COL.BODY - 1]);
    const sched   = data[i][COL.SCHEDULED - 1];
    const status  = String(data[i][COL.STATUS - 1]).trim().toUpperCase();

    if (!to) continue;
    if (status === 'SENT' || status === 'SKIP') continue;           // already handled
    if (sched instanceof Date && sched > now) continue;             // not due yet

    // Duplicate protection: don't email someone already in your Sent mail.
    if (CONFIG.DEDUP_SENT && alreadyEmailed_(to)) {
      sheet.getRange(row, COL.STATUS).setValue('SKIP');
      sheet.getRange(row, COL.SENT_AT).setValue('dedup: already in Sent');
      continue;
    }

    if (CONFIG.DRY_RUN) {
      Logger.log('[DRY_RUN] would send to %s | %s', to, subject);
      sent++;
      continue;
    }

    try {
      const options = { name: CONFIG.FROM_NAME };
      if (CONFIG.FROM_ALIAS) options.from = CONFIG.FROM_ALIAS;
      GmailApp.sendEmail(to, subject, body, options);

      sheet.getRange(row, COL.STATUS).setValue('SENT');
      sheet.getRange(row, COL.SENT_AT).setValue(Utilities.formatDate(now, tz, 'yyyy-MM-dd HH:mm'));
      sent++;
      Logger.log('Sent to %s', to);
      if (sent < CONFIG.DAILY_LIMIT) Utilities.sleep(CONFIG.MIN_GAP_SEC * 1000);
    } catch (err) {
      sheet.getRange(row, COL.STATUS).setValue('ERROR');
      sheet.getRange(row, COL.SENT_AT).setValue(String(err).slice(0, 200));
      Logger.log('ERROR sending to %s: %s', to, err);
    }
  }

  Logger.log('Run complete. Sent %s message(s) this batch.', sent);
}


/** True if there is already a message in Sent addressed to this recipient. */
function alreadyEmailed_(email) {
  const threads = GmailApp.search('in:sent to:' + email, 0, 1);
  return threads.length > 0;
}


// ====================== REPLY MONITOR ======================

/** Run ONCE to install the recurring reply watcher (every N minutes). */
function setupReplyMonitor() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'checkRepliesAndReport') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('checkRepliesAndReport')
    .timeBased()
    .everyMinutes(CONFIG.REPLY_CHECK_EVERY_MIN)
    .create();
  Logger.log('Reply monitor installed: every %s min.', CONFIG.REPLY_CHECK_EVERY_MIN);
}

function removeReplyMonitor() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'checkRepliesAndReport') ScriptApp.deleteTrigger(t);
  });
  Logger.log('Reply monitor removed.');
}

/**
 * Scans for replies from people you've emailed and reports each new one to
 * REPORT_TO. Reports every reply exactly once. Does NOT send any follow-up.
 */
function checkRepliesAndReport() {
  const tz  = Session.getScriptTimeZone();
  const now = new Date();
  const hour = parseInt(Utilities.formatDate(now, tz, 'H'), 10);
  const dow  = parseInt(Utilities.formatDate(now, tz, 'u'), 10) % 7 + 1;

  if (CONFIG.BIZ_DAYS.indexOf(dow) === -1) return;             // not a business day
  if (hour < CONFIG.BIZ_START_HOUR || hour >= CONFIG.BIZ_END_HOUR) return; // outside hours

  const recipients = loadRecipientMap_();                      // email -> {name, company, subject}
  const props = PropertiesService.getScriptProperties();
  let reported = {};
  try { reported = JSON.parse(props.getProperty('REPORTED_IDS') || '{}'); } catch (e) {}

  // Look at recent inbound messages that are not from you.
  const threads = GmailApp.search('in:inbox -from:me newer_than:2d', 0, 50);
  let newCount = 0;

  for (let t = 0; t < threads.length; t++) {
    const msgs = threads[t].getMessages();
    for (let m = 0; m < msgs.length; m++) {
      const msg = msgs[m];
      const id  = msg.getId();
      if (reported[id]) continue;

      const fromAddr = extractEmail_(msg.getFrom()).toLowerCase();
      const match = recipients[fromAddr];
      if (!match) continue;                                    // not one of our prospects
      if (isFromMe_(msg)) continue;

      // It's a genuine reply from a prospect we haven't reported yet.
      const when = Utilities.formatDate(msg.getDate(), tz, 'yyyy-MM-dd HH:mm');
      const summary = msg.getPlainBody().replace(/\s+/g, ' ').trim().slice(0, 400);

      const report =
        'New reply from an outreach prospect.\n\n' +
        'Prospect:      ' + (match.name || '(unknown)') + '\n' +
        'Company:       ' + (match.company || '(n/a)') + '\n' +
        'Email:         ' + fromAddr + '\n' +
        'Their subject: ' + msg.getSubject() + '\n' +
        'Your subject:  ' + (match.subject || '(n/a)') + '\n' +
        'Reply time:    ' + when + '\n\n' +
        'Summary:\n' + summary + '\n\n' +
        '(No follow-up was sent automatically.)';

      GmailApp.sendEmail(CONFIG.REPORT_TO, 'Reply: ' + (match.name || fromAddr) + ' — ' + (match.company || ''), report);

      reported[id] = true;
      newCount++;
    }
  }

  // Keep the processed-id store from growing unbounded.
  const keys = Object.keys(reported);
  if (keys.length > 2000) {
    const trimmed = {};
    keys.slice(keys.length - 1500).forEach(function (k) { trimmed[k] = true; });
    reported = trimmed;
  }
  props.setProperty('REPORTED_IDS', JSON.stringify(reported));
  if (newCount) Logger.log('Reported %s new repl(y/ies).', newCount);
}

/** Build email -> {name, company, subject} from the Outreach sheet. */
function loadRecipientMap_() {
  const sheet = SpreadsheetApp.getActive().getSheetByName(CONFIG.SHEET_NAME);
  const map = {};
  if (!sheet || sheet.getLastRow() < 2) return map;
  const data = sheet.getRange(2, 1, sheet.getLastRow() - 1, COL.THREAD_ID).getValues();
  for (let i = 0; i < data.length; i++) {
    const email = String(data[i][COL.TO - 1]).trim().toLowerCase();
    if (!email) continue;
    map[email] = {
      name:    String(data[i][COL.NAME - 1] || ''),
      company: String(data[i][COL.KIND - 1] || ''), // Kind col; swap to a Company col if you add one
      subject: String(data[i][COL.SUBJECT - 1] || ''),
    };
  }
  return map;
}

function extractEmail_(headerValue) {
  const m = String(headerValue).match(/[\w.+-]+@[\w-]+\.[\w.-]+/);
  return m ? m[0] : String(headerValue);
}

function isFromMe_(msg) {
  const me = Session.getActiveUser().getEmail().toLowerCase();
  return extractEmail_(msg.getFrom()).toLowerCase() === me;
}


/** Optional helper: send a single test email to yourself to verify setup. */
function sendTestToSelf() {
  const me = Session.getActiveUser().getEmail();
  const options = { name: CONFIG.FROM_NAME };
  if (CONFIG.FROM_ALIAS) options.from = CONFIG.FROM_ALIAS;
  GmailApp.sendEmail(me, 'Outreach test', 'If you can read this, the script can send mail.', options);
  Logger.log('Test sent to %s', me);
}
