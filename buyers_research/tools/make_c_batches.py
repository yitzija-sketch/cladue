#!/usr/bin/env python3
"""Build the Workstream-C (entity discovery) batches from the consolidated CSVs.

Picks the N most active buyers from buyer_activity_rank.csv (default 100), skipping unnamed buyers,
buyers confirmed not active in NJ, and the broker's existing call-list buyers (whose entities the local
tax-roll graph already resolved), and groups them 5 per agent with context: buyer type, HQ, deal towns/
years/prices seen in deals_public_2019_2024.csv, SPV names already named in press, and entities already
captured in buyer_entities.csv (so agents do not repeat them).

Writes parts/_runs/C_BATCHES.json = [{"key": "C_01", "buyers": [{"name", "type", "context"}]}, ...]
Run: python3 -I buyers_research/tools/make_c_batches.py [N] [per_batch]
"""
import csv
import json
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = int(sys.argv[1]) if len(sys.argv) > 1 else 100
PER = int(sys.argv[2]) if len(sys.argv) > 2 else 5
CALL_LIST = {'CENTERPOINT PROPERTIES', 'TERRENO REALTY', 'CABOT PROPERTIES', 'SITEX GROUP', 'ELBERON DEVELOPMENT GROUP', 'KURV INDUSTRIAL', 'BRIDGE INDUSTRIAL'}
UNNAMED = ('UNNAMED', 'PRIVATE INVESTOR', 'PRIVATE BUYER', 'JOINT VENTURE', 'UNDISCLOSED', 'LOCAL PARTNERS')


def rd(name):
    with open(os.path.join(ROOT, name), encoding='utf-8') as f:
        return list(csv.DictReader(f))


rank = rd('buyer_activity_rank.csv')
buyers = {r['name_key']: r for r in rd('buyers_stated.csv')}
deals = rd('deals_public_2019_2024.csv')
ents = defaultdict(list)
if os.path.exists(os.path.join(ROOT, 'buyer_entities.csv')):
    for r in rd('buyer_entities.csv'):
        ents[r['name_key']].append(r['entity_name'])

by_buyer = defaultdict(list)
spvs = defaultdict(set)
for d in deals:
    k = d['buyer_name_key']
    if not k or d['address'].upper().startswith('PORTFOLIO'):
        continue
    by_buyer[k].append(d)
    if d.get('buyer_spv_named'):
        spvs[k].add(d['buyer_spv_named'])

chosen = []
for r in rank:
    k = r['name_key']
    if not k or any(u in k for u in UNNAMED) or k in CALL_LIST:
        continue
    b = buyers.get(k, {})
    if b.get('nj_active', '').lower() == 'no':
        continue
    if r['in_buyers_stated'] != 'yes' and int(r['press_deal_rows_2019_2024'] or 0) < 2:
        continue  # one-off deal buyers without a buyer row are low value for entity hunting
    chosen.append((k, r, b))
    if len(chosen) >= N:
        break

batches = []
for i in range(0, len(chosen), PER):
    items = []
    for k, r, b in chosen[i:i + PER]:
        ds = sorted(by_buyer.get(k, []), key=lambda d: d.get('date') or '', reverse=True)[:6]
        dtxt = '; '.join(f"{d['address']}, {d['town']} ({(d.get('date') or '')[:4] or 'n/d'}{', $' + d['price'] if d.get('price') else ''})" for d in ds)
        ctx = []
        if b.get('buyer_type'):
            ctx.append(f"type {b['buyer_type']}")
        if b.get('hq_city'):
            ctx.append(f"HQ {b['hq_city']}, {b.get('hq_state', '')}".strip(', '))
        if b.get('website'):
            ctx.append(b['website'])
        if dtxt:
            ctx.append('NJ deals seen: ' + dtxt)
        if spvs.get(k):
            ctx.append('SPV names already seen in press: ' + '; '.join(sorted(spvs[k]))[:400])
        if ents.get(k):
            ctx.append('entities already recorded (do not repeat): ' + '; '.join(ents[k][:12])[:400])
        items.append({'name': b.get('buyer_name') or r.get('buyer_name') or k.title(), 'type': b.get('buyer_type', ''), 'context': ' | '.join(ctx)[:1500]})
    batches.append({'key': f'C_{i // PER + 1:02d}', 'buyers': items})

out = os.path.join(ROOT, 'parts', '_runs', 'C_BATCHES.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(batches, f, indent=1, ensure_ascii=False)
print(f'{len(chosen)} buyers -> {len(batches)} batches -> {out}')
for b in batches:
    print(b['key'], [x['name'] for x in b['buyers']])
