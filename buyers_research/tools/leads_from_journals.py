#!/usr/bin/env python3
"""Collect each agent's blocked / thin_coverage / not_found / new_buyers_seen / notes from the workflow
journals into parts/_runs/LEADS.json keyed by part key (e.g. "B_year_2021"), so the next research batch
can be pointed at exactly the gaps the previous pass reported.

Run: python3 -I buyers_research/tools/leads_from_journals.py
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESS = '/root/.claude/projects/-home-user-cladue/11d13300-138f-51de-822b-f9fea5fa0346/subagents/workflows'
journals = glob.glob(os.path.join(SESS, 'wf_*', 'journal.jsonl')) + glob.glob(os.path.join(ROOT, 'parts', '_runs', 'wf_*', 'journal.jsonl'))

leads = {}
for jf in journals:
    for line in open(jf, encoding='utf-8', errors='replace'):
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if o.get('type') != 'result' or not isinstance(o.get('result'), dict):
            continue
        r = o['result']
        pf = r.get('part_file', '')
        key = os.path.splitext(os.path.basename(pf))[0] if pf else o.get('label', '').split(':')[-1]
        if not key:
            continue
        parts = []
        for f in ('not_found', 'thin_coverage', 'new_buyers_seen', 'blocked'):
            v = r.get(f)
            if isinstance(v, list) and v:
                items = [str(x) for x in v if 'budget' not in str(x).lower()][:40]
                if items:
                    parts.append(f.upper() + ': ' + ' | '.join(items))
        n = r.get('notes')
        if n:
            parts.append('PREVIOUS NOTES: ' + str(n)[:2500])
        txt = '\n'.join(parts)
        prev = leads.get(key, '')
        leads[key] = (prev + '\n' + txt).strip() if prev else txt

out = os.path.join(ROOT, 'parts', '_runs', 'LEADS.json')
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w', encoding='utf-8') as f:
    json.dump(leads, f, indent=1, ensure_ascii=False)
print(json.dumps({k: len(v) for k, v in leads.items()}, indent=1))
