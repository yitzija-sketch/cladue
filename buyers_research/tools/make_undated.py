#!/usr/bin/env python3
"""Write the still-undated deal rows (from the consolidated CSV) into N JSONL files for a dating pass
by tools/workflows/nj-verify-v.js, skipping rows that already have a date verdict in parts/V_verify.

Run: python3 -I buyers_research/tools/make_undated.py [n_files] [min_price]
"""
import csv
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = int(sys.argv[1]) if len(sys.argv) > 1 else 5
MINP = float(sys.argv[2]) if len(sys.argv) > 2 else 0

rows = list(csv.DictReader(open(os.path.join(ROOT, 'deals_public_2019_2024.csv'), encoding='utf-8')))
already = set()
for fn in glob.glob(os.path.join(ROOT, 'parts', 'V_verify', '*.jsonl')):
    for line in open(fn, encoding='utf-8'):
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if o.get('workstream') == 'B' and o.get('field') == 'date':
            already.add(o.get('row_key', '').strip().upper())

und = [r for r in rows if not r['date'] and not r['address'].upper().startswith('PORTFOLIO')
       and f"{r['address']}, {r['town']}".strip().upper() not in already
       and (not MINP or (r['price'] and float(r['price']) >= MINP))]
# biggest / best-identified first: priced rows by price, then rows with SF, then the rest
und.sort(key=lambda r: (-(float(r['price']) if r['price'] else 0), -(float(r['sf']) if r['sf'] else 0)))
out_dir = os.path.join(ROOT, 'parts', '_runs', 'UNDATED_B')
os.makedirs(out_dir, exist_ok=True)
existing = len(glob.glob(os.path.join(out_dir, 'undated_*.jsonl')))
per = (len(und) + N - 1) // N if und else 0
paths = []
for i in range(N):
    chunk = und[i * per:(i + 1) * per]
    if not chunk:
        break
    p = os.path.join(out_dir, f'undated_{existing + i + 1}.jsonl')
    with open(p, 'w', encoding='utf-8') as f:
        for r in chunk:
            f.write(json.dumps({k: r[k] for k in ('address', 'town', 'county', 'buyer', 'seller', 'sf', 'price',
                                                   'property_type', 'deal_type', 'source_url', 'notes')}, ensure_ascii=False) + '\n')
    paths.append((p, len(chunk)))
print(f'{len(und)} undated rows (not yet date-checked) -> {len(paths)} files')
for p, n in paths:
    print(p, n)
