#!/usr/bin/env python3
"""Build verification targets (args.targets for tools/workflows/nj-verify-v.js) from the part files.

Writes parts/_runs/V_TARGETS.json = [{key, workstream, source, sample, selection}, ...]
Run: python3 -I buyers_research/tools/make_v_targets.py
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = os.path.join(ROOT, 'parts')
targets = []

A_SEL = ('Select rows that carry a stated buy box or a person: any of min_sf, max_sf, min_price, max_price, stated_criteria_quote, acquisitions_head_name non-empty; prefer confidence "high"/"med" rows and rows whose nj_active is "yes". '
         'For each, check: the quote wording exists on the cited domain (search the quoted phrase in quotes with allowed_domains set to that domain); the SF/price band matches; the named person holds that title at that firm; nj_active is supported by at least one NJ deal.')
for fn in sorted(glob.glob(os.path.join(PARTS, 'A_buyers', '*.jsonl'))):
    if os.path.getsize(fn) == 0:
        continue
    targets.append({'key': 'V_' + os.path.splitext(os.path.basename(fn))[0], 'workstream': 'A', 'source': fn, 'sample': 10, 'selection': A_SEL})

B_SEL = ('Select rows in this priority order: price >= 10000000; then rows with cap_rate or buyer_spv_named; then rows whose notes say DATE UNVERIFIED and price >= 3000000 (for these the main job is to find the sale year: search the address + town + "sold"/"acquires" and record field "date" with corrected_value = the year or full date when a source states it). '
         'For each, check buyer, price, sf and year against the cited domain and one independent source.')
for fn in sorted(glob.glob(os.path.join(PARTS, 'B_deals', '*.jsonl'))):
    if os.path.getsize(fn) == 0:
        continue
    targets.append({'key': 'V_' + os.path.splitext(os.path.basename(fn))[0], 'workstream': 'B', 'source': fn, 'sample': 8, 'selection': B_SEL})

C_SEL = ('Select rows with entity_role "SPV" or "fund" first (these are the ones the broker will join to tax records), then "manager"/"GP". '
         'For each, check that the entity is tied to that buyer on the cited domain (search the exact entity name in quotes with allowed_domains set to that domain, then an open search of the entity name + "LLC" + New Jersey) and that the address/state, if given, appear in a source.')
for fn in sorted(glob.glob(os.path.join(PARTS, 'C_entities', '*.jsonl'))):
    if os.path.getsize(fn) == 0:
        continue
    targets.append({'key': 'V_' + os.path.splitext(os.path.basename(fn))[0], 'workstream': 'C', 'source': fn, 'sample': 8, 'selection': C_SEL})

out = os.path.join(PARTS, '_runs', 'V_TARGETS.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(targets, f, indent=1)
print(f'{len(targets)} targets -> {out}')
for t in targets:
    print(t['key'], t['workstream'], t['sample'])
