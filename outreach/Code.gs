/**
 * Eretz Realty — AI Inside-Sales Outreach Machine (Google Apps Script)
 * --------------------------------------------------------------------
 * Runs inside your own Google account. Three automated jobs:
 *
 *   1. sendBatch()              — every 10 min in business hours, sends up to
 *                                 MAX_PER_RUN emails. BEFORE each send it
 *                                 searches Gmail (by email, domain, company)
 *                                 and picks the right behaviour:
 *                                   no history      -> COLD template
 *                                   sent, no reply  -> FOLLOWUP template
 *                                   replied before  -> WARM template
 *                                   active thread   -> skip (don't blast)
 *                                   replied recently-> skip + mark REPLIED
 *                                   unsubscribed    -> suppress forever
 *   2. checkRepliesAndReport()  — every 10 min, detects replies, labels them
 *                                 (Hot Lead / Replied / No Interest), fires an
 *                                 INSTANT alert to REPORT_TO for hot leads, and
 *                                 queues everything for the nightly digest.
 *   3. sendDailyDigest()        — once a day, emails one recap of all replies.
 *
 * It NEVER sends a follow-up automatically in response to a reply.
 *
 * SETUP: see README.md. Quick version:
 *   import recipients.csv -> tab "Outreach"; paste this in Apps Script;
 *   set DRY_RUN=true and test; then run setupAll() once and grant access.
 */

// ============================= CONFIG =============================
const CONFIG = {
  SHEET_NAME:   'Outreach',

  // -- sending pace --
  MAX_PER_RUN:  2,            // emails per run (spec: max 2 every 10 min)
  SEND_EVERY_MIN: 10,         // how often the sender runs
  MIN_GAP_SEC:  30,           // pause between the sends within a run
  BIZ_START_HOUR: 9,          // only send/report between these hours (account TZ)
  BIZ_END_HOUR:   17,
  BIZ_DAYS:     [2, 3, 4, 5, 6], // 1=Sun..7=Sat ; Mon-Fri = [2,3,4,5,6]

  // -- identity --
  FROM_ALIAS:   '',           // '' = default; or a verified send-as alias e.g. 'yitzi@eretzltd.com'
  FROM_NAME:    'Yitzi Jachimowitz',
  SIGNATURE:    'Best,\nYitzi Jachimowitz\nEretz Realty\n347-971-1241 | yitzi@eretzltd.com',

  // -- history logic --
  RECENT_REPLY_DAYS: 120,     // if they replied within this window, do NOT cold-blast
  ACTIVE_THREAD_DAYS: 14,     // any message either way within this window = active, skip

  // -- reply monitor --
  REPORT_TO:    'yitzi@eretzltd.com',
  REPLY_CHECK_EVERY_MIN: 10,
  DIGEST_HOUR:  18,           // nightly digest send hour
  HOT_KEYWORDS: ['interested','need space','call me','send options','budget',
                 'timing','available','requirement','looking for','let\'s talk',
                 'lets talk','sq ft','sf','square feet','tour','pricing','rate'],
  COLD_KEYWORDS:['not interested','no interest','unsubscribe','remove me','stop',
                 'do not contact','no thanks','not looking','pass'],

  DRY_RUN:      true,         // START TRUE. Flip to false to actually send.
};

// Column layout (1-based) — must match the sheet header row.
const COL = { TO:1, NAME:2, COMPANY:3, DOMAIN:4, KIND:5, SUBJECT:6, BODY:7,
              SCHEDULED:8, STATUS:9, SENT_AT:10, TEMPLATE:11, THREAD_ID:12 };

const LABELS = ['Hot Lead', 'Replied', 'No Interest', 'Future Follow Up', 'Needs Call'];
// ==================================================================


/** Install every trigger at once. Run this one function after testing. */
function setupAll() {
  removeAll_();
  ScriptApp.newTrigger('sendBatch').timeBased().everyMinutes(CONFIG.SEND_EVERY_MIN).create();
  ScriptApp.newTrigger('checkRepliesAndReport').timeBased().everyMinutes(CONFIG.REPLY_CHECK_EVERY_MIN).create();
  ScriptApp.newTrigger('sendDailyDigest').timeBased().everyDays(1).atHour(CONFIG.DIGEST_HOUR).create();
  ensureLabels_();
  Logger.log('All triggers installed. DRY_RUN=%s', CONFIG.DRY_RUN);
}

/** Stop all automation. */
function stopAll() { removeAll_(); Logger.log('All triggers removed.'); }

function removeAll_() {
  ScriptApp.getProjectTriggers().forEach(function (t) { ScriptApp.deleteTrigger(t); });
}


// =========================== SENDER ===========================

function sendBatch() {
  if (!inBusinessWindow_()) return;
  const sheet = mustSheet_();
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return;

  const data = sheet.getRange(2, 1, lastRow - 1, COL.THREAD_ID).getValues();
  const now = new Date();
  let sent = 0;

  for (let i = 0; i < data.length && sent < CONFIG.MAX_PER_RUN; i++) {
    const row = i + 2;
    const r = readRow_(data[i]);
    if (!r.to) continue;
    if (['SENT','SKIP','UNSUB','REPLIED','DONE'].indexOf(r.status) !== -1) continue;
    if (r.scheduled instanceof Date && r.scheduled > now) continue;

    // ---- pre-send Gmail history check ----
    const h = gmailHistory_(r.to, r.domain, r.company);

    if (h.unsubscribed) { mark_(sheet, row, 'UNSUB', 'suppressed: opt-out detected'); applyLabel_(r.to, 'No Interest'); continue; }
    if (h.repliedRecently) { mark_(sheet, row, 'REPLIED', 'they replied within ' + CONFIG.RECENT_REPLY_DAYS + 'd'); applyLabel_(r.to, 'Replied'); continue; }
    if (h.activeThread) { mark_(sheet, row, '', 'active thread — holding'); continue; } // leave status blank, retry later

    let template;
    if (h.repliedEver)         template = 'WARM';
    else if (h.weEmailed)      template = 'FOLLOWUP';
    else                       template = 'COLD';

    const msg = buildMessage_(template, r);

    if (CONFIG.DRY_RUN) {
      Logger.log('[DRY_RUN] %s -> %s | %s', template, r.to, msg.subject);
      mark_(sheet, row, '', 'DRY_RUN ' + template); sent++; continue;
    }

    try {
      const opts = { name: CONFIG.FROM_NAME };
      if (CONFIG.FROM_ALIAS) opts.from = CONFIG.FROM_ALIAS;
      GmailApp.sendEmail(r.to, msg.subject, msg.body, opts);
      sheet.getRange(row, COL.STATUS).setValue('SENT');
      sheet.getRange(row, COL.SENT_AT).setValue(fmt_(now));
      sheet.getRange(row, COL.TEMPLATE).setValue(template);
      sent++;
      Logger.log('Sent %s to %s', template, r.to);
      if (sent < CONFIG.MAX_PER_RUN) Utilities.sleep(CONFIG.MIN_GAP_SEC * 1000);
    } catch (err) {
      mark_(sheet, row, 'ERROR', String(err).slice(0, 200));
    }
  }
  Logger.log('sendBatch done — %s sent.', sent);
}

/** Search Gmail three ways and summarize the relationship. */
function gmailHistory_(email, domain, company) {
  const out = { weEmailed:false, repliedEver:false, repliedRecently:false,
                activeThread:false, unsubscribed:false };

  // by exact address (most reliable)
  let threads = GmailApp.search('in:anywhere {to:' + email + ' OR from:' + email + '}', 0, 20);

  // by corporate domain (only if not a free provider)
  if (domain) {
    try { threads = threads.concat(GmailApp.search('in:anywhere {to:@' + domain + ' OR from:@' + domain + '}', 0, 10)); } catch (e) {}
  }
  // by company name phrase
  if (company) {
    try { threads = threads.concat(GmailApp.search('in:anywhere "' + company.replace(/"/g,'') + '"', 0, 5)); } catch (e) {}
  }

  const seen = {};
  const now = Date.now();
  const me = (Session.getActiveUser().getEmail() || '').toLowerCase();

  for (let i = 0; i < threads.length; i++) {
    const id = threads[i].getId();
    if (seen[id]) continue; seen[id] = true;
    const msgs = threads[i].getMessages();
    for (let m = 0; m < msgs.length; m++) {
      const from = extractEmail_(msgs[m].getFrom()).toLowerCase();
      const ageD = (now - msgs[m].getDate().getTime()) / 86400000;
      const fromMe = from === me;
      const fromThem = from === email.toLowerCase() || (domain && from.indexOf('@' + domain) !== -1);

      if (fromMe && fromThem) continue;
      if (fromMe) { out.weEmailed = true; if (ageD <= CONFIG.ACTIVE_THREAD_DAYS) out.activeThread = true; }
      if (fromThem) {
        out.repliedEver = true;
        if (ageD <= CONFIG.RECENT_REPLY_DAYS) out.repliedRecently = true;
        if (ageD <= CONFIG.ACTIVE_THREAD_DAYS) out.activeThread = true;
        const txt = (msgs[m].getPlainBody() || '').toLowerCase();
        if (CONFIG.COLD_KEYWORDS.some(function (k) { return txt.indexOf(k) !== -1; })) out.unsubscribed = true;
      }
    }
  }
  return out;
}

/** Build subject + body for the chosen template. */
function buildMessage_(template, r) {
  const name = r.name || 'there';
  if (template === 'COLD') {
    // Use the pre-crafted personalized copy from the sheet.
    return { subject: r.subject, body: r.body };
  }
  if (template === 'FOLLOWUP') {
    return {
      subject: 'Following up — ' + r.subject,
      body: 'Hi ' + name + ',\n\nJust circling back on my note below — did anything come to mind on either requirement? '
          + 'Happy to move quickly if there\'s a fit.\n\n' + CONFIG.SIGNATURE
          + '\n\n----- original note -----\n' + r.body,
    };
  }
  // WARM
  return {
    subject: 'Reconnecting — ' + r.subject,
    body: 'Hi ' + name + ',\n\nGood to be back in touch. I have active requirements in your area right now '
        + '(a 15,000–30,000 SF port-area lease with 4+ docks, and a 120,000–200,000 SF purchase). '
        + 'Anything on your side worth a look, or anyone I should be talking to?\n\n' + CONFIG.SIGNATURE,
  };
}


// ====================== REPLY MONITOR ======================

function checkRepliesAndReport() {
  if (!inBusinessWindow_()) return;
  const tz = Session.getScriptTimeZone();
  const sheet = mustSheet_();
  const recipients = loadRecipientMap_();
  const props = PropertiesService.getScriptProperties();
  let reported = safeJson_(props.getProperty('REPORTED_IDS'), {});
  let digest   = safeJson_(props.getProperty('DIGEST_QUEUE'), []);

  const threads = GmailApp.search('in:inbox -from:me newer_than:2d', 0, 50);
  let hot = 0;

  for (let t = 0; t < threads.length; t++) {
    const msgs = threads[t].getMessages();
    for (let m = 0; m < msgs.length; m++) {
      const msg = msgs[m];
      const id  = msg.getId();
      if (reported[id]) continue;
      const from = extractEmail_(msg.getFrom()).toLowerCase();
      const match = recipients[from];
      if (!match) continue;            // not one of our prospects
      if (isFromMe_(msg)) continue;

      const when = fmt_(msg.getDate());
      const text = (msg.getPlainBody() || '').replace(/\s+/g,' ').trim();
      const summary = text.slice(0, 400);
      const isHot = CONFIG.HOT_KEYWORDS.some(function (k){ return text.toLowerCase().indexOf(k)!==-1; });
      const isCold = CONFIG.COLD_KEYWORDS.some(function (k){ return text.toLowerCase().indexOf(k)!==-1; });

      // label the thread
      applyLabelToThread_(threads[t], 'Replied');
      if (isHot)  applyLabelToThread_(threads[t], 'Hot Lead');
      if (isCold) applyLabelToThread_(threads[t], 'No Interest');

      // mark sheet so we stop emailing them
      setStatusByEmail_(sheet, from, isCold ? 'UNSUB' : 'REPLIED', 'reply ' + when);

      const line = {
        name: match.name || from, company: match.company || '', email: from,
        theirSubject: msg.getSubject(), ourSubject: match.subject || '',
        when: when, summary: summary, hot: isHot, cold: isCold,
      };

      if (isHot && !CONFIG.DRY_RUN) {
        GmailApp.sendEmail(CONFIG.REPORT_TO,
          'HOT LEAD reply: ' + line.name + ' — ' + line.company,
          renderReply_(line) + '\n\nSuggested action: call today.');
        hot++;
      }
      digest.push(line);
      reported[id] = true;
    }
  }

  if (Object.keys(reported).length > 2000) reported = trimObj_(reported, 1500);
  props.setProperty('REPORTED_IDS', JSON.stringify(reported));
  props.setProperty('DIGEST_QUEUE', JSON.stringify(digest));
  if (hot) Logger.log('Fired %s hot-lead alert(s).', hot);
}

/** Nightly recap of every reply since the last digest. */
function sendDailyDigest() {
  const props = PropertiesService.getScriptProperties();
  const digest = safeJson_(props.getProperty('DIGEST_QUEUE'), []);
  if (!digest.length) { Logger.log('Digest: nothing to send.'); return; }

  let body = 'Prospect replies recap (' + fmt_(new Date()) + ')\n'
           + '======================================\n\n';
  const hot = digest.filter(function(d){return d.hot;});
  const cold = digest.filter(function(d){return d.cold;});
  const neutral = digest.filter(function(d){return !d.hot && !d.cold;});

  if (hot.length)     body += '** HOT — act today (' + hot.length + ') **\n' + hot.map(renderReply_).join('\n\n') + '\n\n';
  if (neutral.length) body += '-- Replied (' + neutral.length + ') --\n' + neutral.map(renderReply_).join('\n\n') + '\n\n';
  if (cold.length)    body += '-- Not interested (' + cold.length + ') --\n' + cold.map(renderReply_).join('\n\n') + '\n\n';

  if (!CONFIG.DRY_RUN) {
    GmailApp.sendEmail(CONFIG.REPORT_TO, 'Prospect Replies — ' + fmt_(new Date()).slice(0,10), body);
  } else {
    Logger.log('[DRY_RUN] digest:\n' + body);
  }
  props.deleteProperty('DIGEST_QUEUE');
}

function renderReply_(d) {
  return d.name + (d.company ? ' — ' + d.company : '') + '\n'
       + '  Email:        ' + d.email + '\n'
       + '  Replied:      ' + d.when + '\n'
       + '  Their subject:' + d.theirSubject + '\n'
       + '  Your subject: ' + d.ourSubject + '\n'
       + '  Summary:      ' + d.summary;
}


// =========================== HELPERS ===========================

function inBusinessWindow_() {
  const tz = Session.getScriptTimeZone(), now = new Date();
  const h = parseInt(Utilities.formatDate(now, tz, 'H'), 10);
  const d = parseInt(Utilities.formatDate(now, tz, 'u'), 10) % 7 + 1;
  return CONFIG.BIZ_DAYS.indexOf(d) !== -1 && h >= CONFIG.BIZ_START_HOUR && h < CONFIG.BIZ_END_HOUR;
}
function mustSheet_() {
  const s = SpreadsheetApp.getActive().getSheetByName(CONFIG.SHEET_NAME);
  if (!s) throw new Error('Sheet tab "' + CONFIG.SHEET_NAME + '" not found.');
  return s;
}
function readRow_(arr) {
  return {
    to: String(arr[COL.TO-1]).trim(), name: String(arr[COL.NAME-1]||''),
    company: String(arr[COL.COMPANY-1]||''), domain: String(arr[COL.DOMAIN-1]||'').trim(),
    kind: String(arr[COL.KIND-1]||''), subject: String(arr[COL.SUBJECT-1]||''),
    body: String(arr[COL.BODY-1]||''), scheduled: arr[COL.SCHEDULED-1],
    status: String(arr[COL.STATUS-1]||'').trim().toUpperCase(),
  };
}
function mark_(sheet, row, status, note) {
  if (status !== undefined && status !== '') sheet.getRange(row, COL.STATUS).setValue(status);
  if (note) sheet.getRange(row, COL.SENT_AT).setValue(note);
}
function setStatusByEmail_(sheet, email, status, note) {
  const last = sheet.getLastRow(); if (last < 2) return;
  const tos = sheet.getRange(2, COL.TO, last-1, 1).getValues();
  for (let i = 0; i < tos.length; i++) {
    if (String(tos[i][0]).trim().toLowerCase() === email.toLowerCase()) {
      sheet.getRange(i+2, COL.STATUS).setValue(status);
      if (note) sheet.getRange(i+2, COL.SENT_AT).setValue(note);
      return;
    }
  }
}
function loadRecipientMap_() {
  const sheet = mustSheet_(); const map = {};
  if (sheet.getLastRow() < 2) return map;
  const data = sheet.getRange(2, 1, sheet.getLastRow()-1, COL.THREAD_ID).getValues();
  data.forEach(function (a) {
    const e = String(a[COL.TO-1]).trim().toLowerCase(); if (!e) return;
    map[e] = { name:String(a[COL.NAME-1]||''), company:String(a[COL.COMPANY-1]||''), subject:String(a[COL.SUBJECT-1]||'') };
  });
  return map;
}
function ensureLabels_() { LABELS.forEach(function (n){ if (!GmailApp.getUserLabelByName(n)) GmailApp.createLabel(n); }); }
function applyLabel_(email, labelName) {
  const th = GmailApp.search('in:anywhere {to:' + email + ' OR from:' + email + '}', 0, 1);
  if (th.length) applyLabelToThread_(th[0], labelName);
}
function applyLabelToThread_(thread, labelName) {
  let lab = GmailApp.getUserLabelByName(labelName) || GmailApp.createLabel(labelName);
  thread.addLabel(lab);
}
function extractEmail_(h){ const m=String(h).match(/[\w.+-]+@[\w-]+\.[\w.-]+/); return m?m[0]:String(h); }
function isFromMe_(msg){ return extractEmail_(msg.getFrom()).toLowerCase() === (Session.getActiveUser().getEmail()||'').toLowerCase(); }
function fmt_(d){ return Utilities.formatDate(d, Session.getScriptTimeZone(), 'yyyy-MM-dd HH:mm'); }
function safeJson_(s, dflt){ try { return s ? JSON.parse(s) : dflt; } catch(e){ return dflt; } }
function trimObj_(obj, keep){ const ks=Object.keys(obj).slice(-keep); const o={}; ks.forEach(function(k){o[k]=true;}); return o; }

/** Verify the script can send. Run manually. */
function sendTestToSelf() {
  const me = Session.getActiveUser().getEmail();
  const opts = { name: CONFIG.FROM_NAME }; if (CONFIG.FROM_ALIAS) opts.from = CONFIG.FROM_ALIAS;
  GmailApp.sendEmail(me, 'Outreach machine test', 'Sending works. DRY_RUN=' + CONFIG.DRY_RUN, opts);
}
