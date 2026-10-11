#!/usr/bin/env python3
"""Build per-buyer context packs for the Workstream-E dossiers.

Picks the N most active named buyers (default 25) from buyer_activity_rank.csv, skipping the broker's
existing call-list buyers (CenterPoint, Terreno, Cabot, Sitex, Elberon, Kurv/Bridge Industrial) and
unnamed/private placeholders, and writes for each one parts/_runs/E_CONTEXT/<slug>.json containing its
buyers_stated row, all its deal rows, all its entity rows and the market-stat rows that mention it, plus
parts/_runs/E_TARGETS.json = [{key, slug, name, name_key, context_file}].

Run: python3 -I buyers_research/tools/make_e_context.py [N]
"""
import csv
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = int(sys.argv[1]) if len(sys.argv) > 1 else 25
CALL_LIST = {'CENTERPOINT PROPERTIES', 'TERRENO REALTY', 'CABOT PROPERTIES', 'SITEX GROUP', 'ELBERON DEVELOPMENT GROUP', 'KURV INDUSTRIAL', 'BRIDGE INDUSTRIAL'}
UNNAMED = ('UNNAMED', 'PRIVATE INVESTOR', 'PRIVATE BUYER', 'JOINT VENTURE', 'UNDISCLOSED', 'LOCAL PARTNERS')


def rd(name):
    with open(os.path.join(ROOT, name), encoding='utf-8') as f:
        return list(csv.DictReader(f))


def slug(s):
    s = re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')
    return s[:48]


rank = rd('buyer_activity_rank.csv')
buyers = {r['name_key']: r for r in rd('buyers_stated.csv')}
deals = rd('deals_public_2019_2024.csv')
ents = defaultdict(list)
for r in rd('buyer_entities.csv'):
    ents[r['name_key']].append(r)
market = rd('market_buyer_mix.csv')

by_buyer = defaultdict(list)
for d in deals:
    if d['buyer_name_key']:
        by_buyer[d['buyer_name_key']].append(d)

out_dir = os.path.join(ROOT, 'parts', '_runs', 'E_CONTEXT')
os.makedirs(out_dir, exist_ok=True)
targets = []
for r in rank:
    k = r['name_key']
    if not k or any(u in k for u in UNNAMED) or k in CALL_LIST:
        continue
    b = buyers.get(k)
    if not b or b.get('nj_active', '').lower() == 'no':
        continue
    name = b['buyer_name']
    sl = slug(name)
    ds = sorted(by_buyer.get(k, []), key=lambda d: d.get('date') or '', reverse=True)
    mk = [m for m in market if k.split()[0] in (m.get('notes', '') + ' ' + m.get('metric', '')).upper()][:10]
    pack = {'buyer': b, 'deals_2019_2024': ds, 'entities': ents.get(k, []), 'market_mentions': mk,
            'rank_row': r}
    cf = os.path.join(out_dir, sl + '.json')
    with open(cf, 'w', encoding='utf-8') as f:
        json.dump(pack, f, indent=1, ensure_ascii=False)
    targets.append({'key': 'E_' + sl, 'slug': sl, 'name': name, 'name_key': k, 'context_file': cf,
                    'deals': len(ds), 'entities': len(ents.get(k, []))})
    if len(targets) >= N:
        break

with open(os.path.join(ROOT, 'parts', '_runs', 'E_TARGETS.json'), 'w', encoding='utf-8') as f:
    json.dump(targets, f, indent=1, ensure_ascii=False)
print(f'{len(targets)} dossier targets')
for t in targets:
    print(f"{t['key']}: deals {t['deals']}, entities {t['entities']}")
