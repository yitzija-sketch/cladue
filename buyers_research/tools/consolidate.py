#!/usr/bin/env python3
"""Concatenate, dedupe and validate the research part files into the deliverable CSVs.

Inputs : buyers_research/parts/{A_buyers,B_deals,C_entities,D_market,V_verify}/*.jsonl
Outputs: buyers_research/buyers_stated.csv, deals_public_2019_2024.csv, buyer_entities.csv,
         market_buyer_mix.csv, buyer_activity_rank.csv, rejected_rows.csv, consolidate_report.json

Run:  python3 -I buyers_research/tools/consolidate.py
"""
import csv
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = os.path.join(ROOT, 'parts')

IN_SCOPE_COUNTIES = {'Bergen', 'Burlington', 'Essex', 'Hudson', 'Mercer', 'Middlesex',
                     'Monmouth', 'Morris', 'Passaic', 'Somerset', 'Union'}

# ---------------------------------------------------------------- town -> county (industrial towns, 11 counties)
TOWN_COUNTY = {
    # Bergen
    'CARLSTADT': 'Bergen', 'MOONACHIE': 'Bergen', 'TETERBORO': 'Bergen', 'LITTLE FERRY': 'Bergen',
    'SOUTH HACKENSACK': 'Bergen', 'HACKENSACK': 'Bergen', 'SADDLE BROOK': 'Bergen', 'ELMWOOD PARK': 'Bergen',
    'LODI': 'Bergen', 'GARFIELD': 'Bergen', 'MAHWAH': 'Bergen', 'ENGLEWOOD': 'Bergen', 'NORTHVALE': 'Bergen',
    'NORWOOD': 'Bergen', 'RIDGEFIELD': 'Bergen', 'FAIRVIEW': 'Bergen', 'EAST RUTHERFORD': 'Bergen',
    'LYNDHURST': 'Bergen', 'WOOD-RIDGE': 'Bergen', 'WOOD RIDGE': 'Bergen', 'HASBROUCK HEIGHTS': 'Bergen',
    'PARAMUS': 'Bergen', 'ROCHELLE PARK': 'Bergen', 'FAIR LAWN': 'Bergen', 'OAKLAND': 'Bergen',
    'FRANKLIN LAKES': 'Bergen', 'ALLENDALE': 'Bergen', 'RAMSEY': 'Bergen', 'UPPER SADDLE RIVER': 'Bergen',
    'MONTVALE': 'Bergen', 'PARK RIDGE': 'Bergen', 'WESTWOOD': 'Bergen', 'EMERSON': 'Bergen', 'ORADELL': 'Bergen',
    'BERGENFIELD': 'Bergen', 'DUMONT': 'Bergen', 'CRESSKILL': 'Bergen', 'PALISADES PARK': 'Bergen',
    'EDGEWATER': 'Bergen', 'RUTHERFORD': 'Bergen', 'NORTH ARLINGTON': 'Bergen', 'WALLINGTON': 'Bergen',
    'RIDGEFIELD PARK': 'Bergen', 'BOGOTA': 'Bergen', 'TEANECK': 'Bergen', 'ENGLEWOOD CLIFFS': 'Bergen',
    'FORT LEE': 'Bergen', 'GLEN ROCK': 'Bergen', 'MAYWOOD': 'Bergen', 'MIDLAND PARK': 'Bergen',
    'WALDWICK': 'Bergen', 'WYCKOFF': 'Bergen', 'HILLSDALE': 'Bergen', 'RIVER EDGE': 'Bergen',
    'NEW MILFORD': 'Bergen', 'CLOSTER': 'Bergen', 'HARRINGTON PARK': 'Bergen', 'LEONIA': 'Bergen',
    'LITTLE FALLS': 'Passaic', 'ROCKLEIGH': 'Bergen', 'OLD TAPPAN': 'Bergen', 'SADDLE RIVER': 'Bergen',
    'HO-HO-KUS': 'Bergen', 'RIDGEWOOD': 'Bergen', 'CLIFFSIDE PARK': 'Bergen', 'TENAFLY': 'Bergen',
    # Hudson
    'SECAUCUS': 'Hudson', 'KEARNY': 'Hudson', 'SOUTH KEARNY': 'Hudson', 'HARRISON': 'Hudson',
    'NORTH BERGEN': 'Hudson', 'JERSEY CITY': 'Hudson', 'BAYONNE': 'Hudson', 'HOBOKEN': 'Hudson',
    'UNION CITY': 'Hudson', 'WEST NEW YORK': 'Hudson', 'WEEHAWKEN': 'Hudson', 'GUTTENBERG': 'Hudson',
    'EAST NEWARK': 'Hudson',
    # Essex
    'NEWARK': 'Essex', 'IRVINGTON': 'Essex', 'EAST ORANGE': 'Essex', 'ORANGE': 'Essex', 'WEST ORANGE': 'Essex',
    'SOUTH ORANGE': 'Essex', 'BLOOMFIELD': 'Essex', 'BELLEVILLE': 'Essex', 'NUTLEY': 'Essex',
    'FAIRFIELD': 'Essex', 'WEST CALDWELL': 'Essex', 'CALDWELL': 'Essex', 'LIVINGSTON': 'Essex',
    'CEDAR GROVE': 'Essex', 'VERONA': 'Essex', 'MONTCLAIR': 'Essex', 'MAPLEWOOD': 'Essex', 'MILLBURN': 'Essex',
    'ROSELAND': 'Essex', 'GLEN RIDGE': 'Essex', 'NORTH CALDWELL': 'Essex', 'ESSEX FELLS': 'Essex',
    'SHORT HILLS': 'Essex',
    # Union
    'ELIZABETH': 'Union', 'LINDEN': 'Union', 'HILLSIDE': 'Union', 'UNION': 'Union', 'UNION TOWNSHIP': 'Union',
    'KENILWORTH': 'Union', 'CRANFORD': 'Union', 'RAHWAY': 'Union', 'SPRINGFIELD': 'Union', 'ROSELLE': 'Union',
    'ROSELLE PARK': 'Union', 'GARWOOD': 'Union', 'CLARK': 'Union', 'WESTFIELD': 'Union', 'SCOTCH PLAINS': 'Union',
    'PLAINFIELD': 'Union', 'BERKELEY HEIGHTS': 'Union', 'NEW PROVIDENCE': 'Union', 'SUMMIT': 'Union',
    'MOUNTAINSIDE': 'Union', 'FANWOOD': 'Union', 'WINFIELD': 'Union',
    # Passaic
    'CLIFTON': 'Passaic', 'PASSAIC': 'Passaic', 'PATERSON': 'Passaic', 'TOTOWA': 'Passaic', 'WAYNE': 'Passaic',
    'WOODLAND PARK': 'Passaic', 'HAWTHORNE': 'Passaic', 'HALEDON': 'Passaic', 'PROSPECT PARK': 'Passaic',
    'POMPTON LAKES': 'Passaic', 'WANAQUE': 'Passaic', 'BLOOMINGDALE': 'Passaic', 'NORTH HALEDON': 'Passaic',
    'RINGWOOD': 'Passaic', 'WEST MILFORD': 'Passaic', 'WEST PATERSON': 'Passaic',
    # Middlesex
    'EDISON': 'Middlesex', 'PISCATAWAY': 'Middlesex', 'SOUTH PLAINFIELD': 'Middlesex', 'NEW BRUNSWICK': 'Middlesex',
    'NORTH BRUNSWICK': 'Middlesex', 'SOUTH BRUNSWICK': 'Middlesex', 'CRANBURY': 'Middlesex', 'MONROE': 'Middlesex',
    'MONROE TOWNSHIP': 'Middlesex', 'DAYTON': 'Middlesex', 'JAMESBURG': 'Middlesex', 'SAYREVILLE': 'Middlesex',
    'OLD BRIDGE': 'Middlesex', 'WOODBRIDGE': 'Middlesex', 'AVENEL': 'Middlesex', 'ISELIN': 'Middlesex',
    'KEASBEY': 'Middlesex', 'PORT READING': 'Middlesex', 'SEWAREN': 'Middlesex', 'FORDS': 'Middlesex',
    'COLONIA': 'Middlesex', 'HOPELAWN': 'Middlesex', 'CARTERET': 'Middlesex', 'PERTH AMBOY': 'Middlesex',
    'METUCHEN': 'Middlesex', 'MIDDLESEX': 'Middlesex', 'MIDDLESEX BOROUGH': 'Middlesex', 'DUNELLEN': 'Middlesex',
    'EAST BRUNSWICK': 'Middlesex', 'SPOTSWOOD': 'Middlesex', 'HELMETTA': 'Middlesex', 'MILLTOWN': 'Middlesex',
    'HIGHLAND PARK': 'Middlesex', 'SOUTH AMBOY': 'Middlesex', 'SOUTH RIVER': 'Middlesex', 'PLAINSBORO': 'Middlesex',
    'MONMOUTH JUNCTION': 'Middlesex', 'KENDALL PARK': 'Middlesex', 'PARLIN': 'Middlesex',
    # Somerset
    'SOMERSET': 'Somerset', 'FRANKLIN TOWNSHIP': 'Somerset', 'FRANKLIN': 'Somerset', 'BRANCHBURG': 'Somerset',
    'BRIDGEWATER': 'Somerset', 'HILLSBOROUGH': 'Somerset', 'BOUND BROOK': 'Somerset', 'SOUTH BOUND BROOK': 'Somerset',
    'MANVILLE': 'Somerset', 'WARREN': 'Somerset', 'BERNARDS': 'Somerset', 'BASKING RIDGE': 'Somerset',
    'BERNARDSVILLE': 'Somerset', 'SOMERVILLE': 'Somerset', 'RARITAN': 'Somerset', 'GREEN BROOK': 'Somerset',
    'WATCHUNG': 'Somerset', 'MONTGOMERY': 'Somerset', 'SKILLMAN': 'Somerset', 'BELLE MEAD': 'Somerset',
    'NORTH PLAINFIELD': 'Somerset', 'PEAPACK': 'Somerset', 'FAR HILLS': 'Somerset', 'BEDMINSTER': 'Somerset',
    'ROCKY HILL': 'Somerset',
    # Morris
    'PARSIPPANY': 'Morris', 'PARSIPPANY-TROY HILLS': 'Morris', 'ROCKAWAY': 'Morris', 'DOVER': 'Morris',
    'WHARTON': 'Morris', 'PINE BROOK': 'Morris', 'MONTVILLE': 'Morris', 'WHIPPANY': 'Morris', 'HANOVER': 'Morris',
    'CEDAR KNOLLS': 'Morris', 'RANDOLPH': 'Morris', 'MOUNT OLIVE': 'Morris', 'FLANDERS': 'Morris',
    'BUDD LAKE': 'Morris', 'BOONTON': 'Morris', 'DENVILLE': 'Morris', 'EAST HANOVER': 'Morris',
    'FLORHAM PARK': 'Morris', 'MORRIS PLAINS': 'Morris', 'MORRISTOWN': 'Morris', 'KENVIL': 'Morris',
    'LEDGEWOOD': 'Morris', 'ROXBURY': 'Morris', 'RIVERDALE': 'Morris', 'BUTLER': 'Morris', 'LINCOLN PARK': 'Morris',
    'PEQUANNOCK': 'Morris', 'POMPTON PLAINS': 'Morris', 'MOUNT ARLINGTON': 'Morris', 'TOWACO': 'Morris',
    'FAIRFIELD TOWNSHIP': 'Essex', 'MADISON': 'Morris', 'CHATHAM': 'Morris', 'CHESTER': 'Morris',
    'LANDING': 'Morris', 'SUCCASUNNA': 'Morris', 'NETCONG': 'Morris', 'MINE HILL': 'Morris',
    'LAKE HOPATCONG': 'Morris', 'HACKETTSTOWN': 'Warren', 'LONG VALLEY': 'Morris', 'MORRIS TOWNSHIP': 'Morris',
    'MOUNTAIN LAKES': 'Morris', 'KINNELON': 'Morris',
    # Mercer
    'HAMILTON': 'Mercer', 'HAMILTON TOWNSHIP': 'Mercer', 'ROBBINSVILLE': 'Mercer', 'EWING': 'Mercer',
    'TRENTON': 'Mercer', 'LAWRENCEVILLE': 'Mercer', 'LAWRENCE': 'Mercer', 'LAWRENCE TOWNSHIP': 'Mercer',
    'WEST WINDSOR': 'Mercer', 'EAST WINDSOR': 'Mercer', 'HIGHTSTOWN': 'Mercer', 'PRINCETON': 'Mercer',
    'PENNINGTON': 'Mercer', 'HOPEWELL': 'Mercer', 'PRINCETON JUNCTION': 'Mercer', 'WINDSOR': 'Mercer',
    # Monmouth
    'FREEHOLD': 'Monmouth', 'NEPTUNE': 'Monmouth', 'WALL': 'Monmouth', 'WALL TOWNSHIP': 'Monmouth',
    'FARMINGDALE': 'Monmouth', 'HOWELL': 'Monmouth', 'EATONTOWN': 'Monmouth', 'TINTON FALLS': 'Monmouth',
    'MARLBORO': 'Monmouth', 'MATAWAN': 'Monmouth', 'KEYPORT': 'Monmouth', 'ABERDEEN': 'Monmouth',
    'RED BANK': 'Monmouth', 'SHREWSBURY': 'Monmouth', 'OCEANPORT': 'Monmouth', 'LONG BRANCH': 'Monmouth',
    'MANALAPAN': 'Monmouth', 'ENGLISHTOWN': 'Monmouth', 'MILLSTONE': 'Monmouth', 'ASBURY PARK': 'Monmouth',
    'BELMAR': 'Monmouth', 'HOLMDEL': 'Monmouth', 'MIDDLETOWN': 'Monmouth', 'HAZLET': 'Monmouth',
    'KEANSBURG': 'Monmouth', 'UNION BEACH': 'Monmouth', 'OCEAN TOWNSHIP': 'Monmouth', 'COLTS NECK': 'Monmouth',
    'MANASQUAN': 'Monmouth', 'BRIELLE': 'Monmouth', 'SPRING LAKE': 'Monmouth', 'ALLENTOWN': 'Monmouth',
    'UPPER FREEHOLD': 'Monmouth', 'CLIFFWOOD': 'Monmouth', 'CLIFFWOOD BEACH': 'Monmouth',
    # Burlington
    'BURLINGTON': 'Burlington', 'BURLINGTON TOWNSHIP': 'Burlington', 'BURLINGTON CITY': 'Burlington',
    'FLORENCE': 'Burlington', 'BORDENTOWN': 'Burlington', 'MOUNT LAUREL': 'Burlington', 'MOORESTOWN': 'Burlington',
    'CINNAMINSON': 'Burlington', 'DELANCO': 'Burlington', 'DELRAN': 'Burlington', 'RIVERSIDE': 'Burlington',
    'WESTAMPTON': 'Burlington', 'MOUNT HOLLY': 'Burlington', 'LUMBERTON': 'Burlington', 'EVESHAM': 'Burlington',
    'MARLTON': 'Burlington', 'PEMBERTON': 'Burlington', 'MEDFORD': 'Burlington', 'SOUTHAMPTON': 'Burlington',
    'MANSFIELD': 'Burlington', 'COLUMBUS': 'Burlington', 'SPRINGFIELD TOWNSHIP': 'Burlington',
    'EDGEWATER PARK': 'Burlington', 'WILLINGBORO': 'Burlington', 'PALMYRA': 'Burlington', 'RIVERTON': 'Burlington',
    'MAPLE SHADE': 'Burlington', 'HAINESPORT': 'Burlington', 'EASTAMPTON': 'Burlington', 'CHESTERFIELD': 'Burlington',
    'FIELDSBORO': 'Burlington', 'BEVERLY': 'Burlington', 'SHAMONG': 'Burlington', 'TABERNACLE': 'Burlington',
    'NORTH HANOVER': 'Burlington', 'NEW HANOVER': 'Burlington', 'WRIGHTSTOWN': 'Burlington',
    # common OUT-of-scope towns (so they can be rejected deterministically)
    'PENNSAUKEN': 'Camden', 'CHERRY HILL': 'Camden', 'CAMDEN': 'Camden', 'BELLMAWR': 'Camden', 'GLOUCESTER CITY': 'Camden',
    'VOORHEES': 'Camden', 'BERLIN': 'Camden', 'WINSLOW': 'Camden', 'WEST DEPTFORD': 'Gloucester', 'LOGAN': 'Gloucester',
    'LOGAN TOWNSHIP': 'Gloucester', 'SWEDESBORO': 'Gloucester', 'WOOLWICH': 'Gloucester', 'DEPTFORD': 'Gloucester',
    'GLASSBORO': 'Gloucester', 'PAULSBORO': 'Gloucester', 'MONROE TOWNSHIP GLOUCESTER': 'Gloucester',
    'BRIDGEPORT': 'Gloucester', 'PENNSVILLE': 'Salem', 'CARNEYS POINT': 'Salem', 'SALEM': 'Salem',
    'VINELAND': 'Cumberland', 'MILLVILLE': 'Cumberland', 'BRIDGETON': 'Cumberland',
    'LAKEWOOD': 'Ocean', 'TOMS RIVER': 'Ocean', 'JACKSON': 'Ocean', 'BRICK': 'Ocean', 'LAKEHURST': 'Ocean',
    'MANCHESTER': 'Ocean', 'BARNEGAT': 'Ocean', 'STAFFORD': 'Ocean', 'BERKELEY': 'Ocean',
    'PHILLIPSBURG': 'Warren', 'WASHINGTON': 'Warren', 'LOPATCONG': 'Warren', 'POHATCONG': 'Warren',
    'BELVIDERE': 'Warren', 'MANSFIELD WARREN': 'Warren', 'ALLAMUCHY': 'Warren',
    'FLEMINGTON': 'Hunterdon', 'RARITAN TOWNSHIP': 'Hunterdon', 'CLINTON': 'Hunterdon', 'READINGTON': 'Hunterdon',
    'WHITEHOUSE STATION': 'Hunterdon', 'LAMBERTVILLE': 'Hunterdon', 'LEBANON': 'Hunterdon', 'UNION TOWNSHIP HUNTERDON': 'Hunterdon',
    'FRANKLIN SUSSEX': 'Sussex', 'SPARTA': 'Sussex', 'NEWTON': 'Sussex', 'HOPATCONG': 'Sussex', 'VERNON': 'Sussex',
    'ANDOVER': 'Sussex', 'HAMBURG': 'Sussex',
    'EGG HARBOR': 'Atlantic', 'EGG HARBOR TOWNSHIP': 'Atlantic', 'ATLANTIC CITY': 'Atlantic', 'PLEASANTVILLE': 'Atlantic',
    'HAMMONTON': 'Atlantic', 'GALLOWAY': 'Atlantic',
}

# ---------------------------------------------------------------- normalisation helpers
_SUFFIX_RE = re.compile(r'\b(L\.?\s?L\.?\s?C\.?|L\.?\s?P\.?|L\.?\s?L\.?\s?P\.?)\b', re.I)


def name_key(name):
    """UPPERCASE, punctuation removed, LLC/INC/LP/CORP/THE removed, single-spaced."""
    if not name:
        return ''
    s = str(name).upper()
    s = _SUFFIX_RE.sub(lambda m: m.group(0).replace('.', '').replace(' ', ''), s)
    s = s.replace('&', ' AND ')
    s = re.sub(r'[^A-Z0-9 ]+', ' ', s)
    toks = [t for t in s.split() if t not in {'LLC', 'INC', 'LP', 'LLP', 'CORP', 'THE'}]
    return ' '.join(toks)


_ADDR_SUB = [
    (r'\bAVENUE\b', 'AVE'), (r'\bSTREET\b', 'ST'), (r'\bROAD\b', 'RD'), (r'\bBOULEVARD\b', 'BLVD'),
    (r'\bDRIVE\b', 'DR'), (r'\bLANE\b', 'LN'), (r'\bHIGHWAY\b', 'HWY'), (r'\bROUTE\b', 'RT'), (r'\bRTE\b', 'RT'),
    (r'\bPLACE\b', 'PL'), (r'\bCOURT\b', 'CT'), (r'\bTERRACE\b', 'TER'), (r'\bPARKWAY\b', 'PKWY'),
    (r'\bTURNPIKE\b', 'TPKE'), (r'\bCIRCLE\b', 'CIR'), (r'\bNORTH\b', 'N'), (r'\bSOUTH\b', 'S'),
    (r'\bEAST\b', 'E'), (r'\bWEST\b', 'W'), (r'\bUS\b', ''), (r'\bU S\b', ''),
]


def addr_key(addr):
    if not addr:
        return ''
    s = str(addr).upper()
    s = re.sub(r'[^A-Z0-9 ]+', ' ', s)
    for pat, rep in _ADDR_SUB:
        s = re.sub(pat, rep, s)
    return ' '.join(s.split())


_NUM_RE = re.compile(r'^-?\d+(\.\d+)?$')


def to_number(v, field=''):
    """Coerce money/SF/percent strings to a plain number. Returns (value_or_blank, note)."""
    if v is None:
        return '', ''
    if isinstance(v, bool):
        return '', 'bool->blank'
    if isinstance(v, (int, float)):
        return v, ''
    s = str(v).strip()
    if s == '' or s.lower() in {'n/a', 'na', 'none', 'null', 'undisclosed', 'unknown', '-', '--', 'tbd'}:
        return '', ''
    orig = s
    s = s.replace(',', '').replace('$', '').replace('%', '').replace('+', '')
    s = re.sub(r'(?i)\b(sf|sq\.?\s*ft\.?|square feet|acres?|ac|psf|per sf|/sf|usd|approximately|approx\.?|about|~)\b', '', s)
    s = s.strip()
    mult = 1
    m = re.match(r'(?i)^(-?\d+(?:\.\d+)?)\s*(mm|m|million|k|thousand|b|billion)?$', s)
    if m:
        num = float(m.group(1))
        suf = (m.group(2) or '').lower()
        if suf in {'mm', 'm', 'million'}:
            mult = 1_000_000
        elif suf in {'k', 'thousand'}:
            mult = 1_000
        elif suf in {'b', 'billion'}:
            mult = 1_000_000_000
        val = num * mult
        if field in {'sf', 'price', 'loan_amount', 'min_sf', 'max_sf', 'min_price', 'max_price', 'year_built', 'nj_deal_count_seen'}:
            val = int(round(val))
        elif val == int(val):
            val = int(val)
        return val, ''
    # ranges such as "100,000-250,000" -> take low value and note
    m = re.match(r'^(-?\d+(?:\.\d+)?)\s*(?:-|to|–)\s*(-?\d+(?:\.\d+)?)$', s)
    if m:
        return float(m.group(1)) if '.' in m.group(1) else int(m.group(1)), f'{field} range "{orig}" -> low value kept'
    return '', f'{field} non-numeric "{orig}" blanked'


_MONTHS = {m: i for i, m in enumerate(['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'], 1)}


def norm_date(v):
    """Return (YYYY | YYYY-MM | YYYY-MM-DD, note)."""
    if v is None:
        return '', ''
    s = str(v).strip()
    if not s or s.lower() in {'n/a', 'na', 'none', 'null', 'unknown', 'undated', ''}:
        return '', ''
    s2 = s.replace('/', '-').replace('.', '-')
    m = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})', s2)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12 and 1 <= d <= 31:
            return f'{y:04d}-{mo:02d}-{d:02d}', ''
    m = re.match(r'^(\d{4})-(\d{1,2})$', s2)
    if m and 1 <= int(m.group(2)) <= 12:
        return f'{int(m.group(1)):04d}-{int(m.group(2)):02d}', ''
    m = re.match(r'^(\d{4})$', s2)
    if m:
        return m.group(1), ''
    m = re.match(r'^(\d{1,2})-(\d{1,2})-(\d{4})$', s2)  # MM-DD-YYYY
    if m:
        mo, d, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12 and 1 <= d <= 31:
            return f'{y:04d}-{mo:02d}-{d:02d}', ''
    m = re.match(r'(?i)^([a-z]{3})[a-z]*\.?\s+(\d{1,2}),?\s+(\d{4})$', s)  # March 5, 2021
    if m and m.group(1).lower() in _MONTHS:
        return f'{int(m.group(3)):04d}-{_MONTHS[m.group(1).lower()]:02d}-{int(m.group(2)):02d}', ''
    m = re.match(r'(?i)^(\d{1,2})\s+([a-z]{3})[a-z]*\.?\s+(\d{4})$', s)  # 5 March 2021
    if m and m.group(2).lower() in _MONTHS:
        return f'{int(m.group(3)):04d}-{_MONTHS[m.group(2).lower()]:02d}-{int(m.group(1)):02d}', ''
    m = re.match(r'(?i)^([a-z]{3})[a-z]*\.?\s+(\d{4})$', s)  # March 2021
    if m and m.group(1).lower() in _MONTHS:
        return f'{int(m.group(2)):04d}-{_MONTHS[m.group(1).lower()]:02d}', ''
    m = re.match(r'(?i)^q([1-4])\s+(\d{4})$', s)  # Q3 2021 -> first month of quarter
    if m:
        return f'{int(m.group(2)):04d}-{(int(m.group(1)) - 1) * 3 + 1:02d}', f'quarter date "{s}" -> first month'
    m = re.search(r'(20\d{2})', s)
    if m:
        return m.group(1), f'date "{s}" reduced to year'
    return '', f'date "{s}" unparseable, blanked'


def year_of(d):
    m = re.match(r'^(\d{4})', d or '')
    return int(m.group(1)) if m else None


def blank(v):
    return v is None or (isinstance(v, str) and v.strip() == '')


def s(v):
    if v is None:
        return ''
    if isinstance(v, (list, tuple)):
        return '; '.join(str(x) for x in v if x not in (None, ''))
    if isinstance(v, dict):
        return json.dumps(v, ensure_ascii=False)
    return str(v).strip()


def ok_url(u):
    u = s(u)
    return bool(re.match(r'^https?://[^\s]+$', u))


# ---------------------------------------------------------------- reading
def read_parts(sub):
    rows = []
    bad = Counter()
    for fn in sorted(glob.glob(os.path.join(PARTS, sub, '*.jsonl'))):
        part = os.path.basename(fn)
        with open(fn, encoding='utf-8', errors='replace') as f:
            buf = ''
            for line in f:
                line = line.strip()
                if not line or line in ('[', ']'):
                    continue
                buf += line
                try:
                    obj = json.loads(buf.rstrip(','))
                    buf = ''
                except json.JSONDecodeError:
                    # tolerate pretty-printed multi-line objects
                    if len(buf) > 200_000:
                        bad[part] += 1
                        buf = ''
                    continue
                if isinstance(obj, list):
                    for o in obj:
                        if isinstance(o, dict):
                            o['_part'] = part
                            rows.append(o)
                elif isinstance(obj, dict):
                    obj['_part'] = part
                    rows.append(obj)
            if buf:
                bad[part] += 1
    return rows, bad


def merge_group(rows, text_fields, conf_field='confidence'):
    """Merge duplicate rows: prefer the row with the most filled fields; fill blanks from the others."""
    rows = sorted(rows, key=lambda r: -sum(1 for k, v in r.items() if not blank(v) and not k.startswith('_')))
    base = dict(rows[0])
    notes = []
    srcs = []
    parts = []
    conf_rank = {'high': 3, 'med': 2, 'medium': 2, 'low': 1}
    for r in rows:
        parts.append(r.get('_part', ''))
        for k, v in r.items():
            if k.startswith('_'):
                continue
            if blank(base.get(k)) and not blank(v):
                base[k] = v
        n = s(r.get('notes'))
        if n and n not in notes:
            notes.append(n)
        for uf in ('source_url', 'criteria_source_url', 'evidence_url'):
            u = s(r.get(uf))
            if u and u not in srcs:
                srcs.append(u)
        if conf_rank.get(s(r.get(conf_field)).lower(), 0) > conf_rank.get(s(base.get(conf_field)).lower(), 0):
            base[conf_field] = r.get(conf_field)
    base['notes'] = ' | '.join(notes)[:2000]
    base['_parts'] = ';'.join(sorted(set(p for p in parts if p)))
    base['_all_source_urls'] = ' '.join(srcs)[:2000]
    base['_dupes_merged'] = len(rows) - 1
    return base


# ---------------------------------------------------------------- verification overlay
def load_verifications():
    rows, _ = read_parts('V_verify')
    by_ws = defaultdict(list)
    for r in rows:
        ws = s(r.get('workstream')).upper()[:1]
        if ws in {'A', 'B', 'C', 'D'}:
            by_ws[ws].append(r)
    return by_ws


def apply_verification(row, vrows, key_fn):
    tags = []
    rk = key_fn(row)
    for v in vrows:
        vk = name_key(s(v.get('row_key')))
        if not vk or vk != rk:
            continue
        verdict = s(v.get('verdict')).lower()
        field = s(v.get('field'))
        note = s(v.get('note'))[:200]
        corrected = v.get('corrected_value')
        if verdict == 'confirmed':
            tags.append(f'confirmed:{field or "row"}')
        elif verdict == 'refuted':
            if field and field in row:
                if not blank(corrected):
                    row[field] = corrected
                    tags.append(f'corrected:{field}')
                else:
                    row[field] = ''
                    tags.append(f'refuted-blanked:{field}')
            else:
                tags.append('refuted:row')
                row['confidence'] = 'low'
            if note:
                row['notes'] = (s(row.get('notes')) + f' | VERIFY: {note}').strip(' |')
        elif verdict == 'unverifiable':
            tags.append(f'unverifiable:{field or "row"}')
    row['verification'] = ';'.join(tags)
    return row


# ---------------------------------------------------------------- workstreams
A_COLS = ['buyer_name', 'name_key', 'parent', 'buyer_type', 'hq_address', 'hq_city', 'hq_state', 'nj_office_address',
          'website', 'min_sf', 'max_sf', 'min_price', 'max_price', 'building_age_pref', 'clear_height_pref',
          'product_types', 'target_submarkets', 'tenancy_pref', 'hold_strategy', 'equity_source', 'deal_structures',
          'stated_criteria_quote', 'criteria_source_url', 'criteria_date', 'acquisitions_head_name',
          'acquisitions_head_title', 'work_email_or_pattern', 'phone', 'linkedin', 'confidence', 'notes',
          'nj_active', 'nj_deal_count_seen', 'source_url', 'verification', 'source_parts', 'dupes_merged']
A_NUM = ['min_sf', 'max_sf', 'min_price', 'max_price', 'nj_deal_count_seen']
A_TYPES = {'reit', 'open-end fund', 'closed-end pe', 'family office', 'developer-holder', 'owner-user', 'ios specialist', 'other'}

B_COLS = ['date', 'address', 'town', 'county', 'buyer', 'buyer_name_key', 'buyer_parent', 'buyer_spv_named', 'seller',
          'seller_name_key', 'seller_parent', 'sf', 'acres', 'price', 'price_psf', 'cap_rate', 'property_type',
          'year_built', 'occupancy_at_sale', 'tenant', 'lender', 'loan_amount', 'brokers', 'deal_type',
          'portfolio_context', 'source_url', 'source_date', 'confidence', 'notes', 'verification', 'source_parts',
          'dupes_merged']
B_NUM = ['sf', 'acres', 'price', 'price_psf', 'cap_rate', 'year_built', 'occupancy_at_sale', 'loan_amount']

C_COLS = ['buyer_name', 'name_key', 'entity_name', 'entity_name_key', 'entity_role', 'state_of_formation',
          'mailing_or_registered_address', 'signatory_or_officer_names', 'evidence_type', 'evidence_url', 'confidence',
          'notes', 'verification', 'source_parts', 'dupes_merged']

D_COLS = ['year', 'quarter', 'submarket', 'size_band', 'metric', 'value', 'unit', 'source_name', 'source_url',
          'source_date', 'notes', 'source_parts']


def write_csv(path, cols, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow({c: s(r.get(c)) for c in cols})


def finish(row):
    row['source_parts'] = row.pop('_parts', row.get('_part', ''))
    row['dupes_merged'] = row.pop('_dupes_merged', 0)
    return row


def consolidate():
    report = {}
    rejected = []
    ver = load_verifications()

    # ---------------- A
    raw, bad = read_parts('A_buyers')
    report['A_raw_rows'] = len(raw)
    report['A_unparseable_blocks'] = dict(bad)
    groups = defaultdict(list)
    for r in raw:
        nm = s(r.get('buyer_name'))
        if not nm:
            rejected.append({'file': 'A', 'part': r.get('_part'), 'reason': 'empty buyer_name', 'row': json.dumps(r)[:500]})
            continue
        r['name_key'] = name_key(nm)
        if blank(r.get('source_url')):
            r['source_url'] = r.get('criteria_source_url') or ''
        groups[r['name_key']].append(r)
    a_rows = []
    for k, rs in groups.items():
        m = merge_group(rs, A_COLS)
        notes = []
        for f in A_NUM:
            v, n = to_number(m.get(f), f)
            m[f] = v
            if n:
                notes.append(n)
        d, n = norm_date(m.get('criteria_date'))
        m['criteria_date'] = d
        if n:
            notes.append(n)
        bt = s(m.get('buyer_type')).lower()
        if bt and bt not in A_TYPES:
            notes.append(f'buyer_type "{m.get("buyer_type")}" not in vocabulary')
            m['buyer_type'] = 'other'
        if not ok_url(m.get('source_url')):
            if ok_url(m.get('criteria_source_url')):
                m['source_url'] = m['criteria_source_url']
            else:
                rejected.append({'file': 'A', 'part': m.get('_parts'), 'reason': 'no valid source_url', 'row': json.dumps({k2: s(v2) for k2, v2 in m.items()})[:800]})
                continue
        if notes:
            m['notes'] = (s(m.get('notes')) + ' | VALIDATION: ' + '; '.join(notes)).strip(' |')
        apply_verification(m, ver.get('A', []), lambda r: r['name_key'])
        a_rows.append(finish(m))
    a_rows.sort(key=lambda r: (-(r.get('nj_deal_count_seen') or 0) if isinstance(r.get('nj_deal_count_seen'), (int, float)) else 0, r['name_key']))
    write_csv(os.path.join(ROOT, 'buyers_stated.csv'), A_COLS, a_rows)
    report['A_rows'] = len(a_rows)
    report['A_with_stated_criteria'] = sum(1 for r in a_rows if any(not blank(r.get(f)) for f in ('min_sf', 'max_sf', 'min_price', 'max_price', 'stated_criteria_quote')))
    report['A_by_type'] = dict(Counter(s(r.get('buyer_type')) for r in a_rows))
    report['A_nj_active'] = dict(Counter(s(r.get('nj_active')).lower() for r in a_rows))

    # ---------------- B
    raw, bad = read_parts('B_deals')
    report['B_raw_rows'] = len(raw)
    report['B_unparseable_blocks'] = dict(bad)
    groups = defaultdict(list)
    for r in raw:
        d, n1 = norm_date(r.get('date'))
        sd, n2 = norm_date(r.get('source_date'))
        r['date'], r['source_date'] = d, sd
        r['_vnotes'] = [x for x in (n1, n2) if x]
        town = s(r.get('town'))
        tk = town.upper().replace(' TWP', ' TOWNSHIP').replace(', NJ', '').strip()
        county = s(r.get('county')).replace(' County', '').strip().title()
        if tk in TOWN_COUNTY:
            if county != TOWN_COUNTY[tk]:
                if county:
                    r['_vnotes'].append(f'county "{county}" corrected to {TOWN_COUNTY[tk]} from town')
                county = TOWN_COUNTY[tk]
        r['county'] = county
        y = year_of(d) or year_of(sd)
        if y and (y < 2019 or y > 2024):
            rejected.append({'file': 'B', 'part': r.get('_part'), 'reason': f'outside 2019-2024 ({y})', 'row': json.dumps({k: s(v) for k, v in r.items()})[:800]})
            continue
        if county and county not in IN_SCOPE_COUNTIES:
            rejected.append({'file': 'B', 'part': r.get('_part'), 'reason': f'county out of scope ({county})', 'row': json.dumps({k: s(v) for k, v in r.items()})[:800]})
            continue
        if not ok_url(r.get('source_url')):
            rejected.append({'file': 'B', 'part': r.get('_part'), 'reason': 'no valid source_url', 'row': json.dumps({k: s(v) for k, v in r.items()})[:800]})
            continue
        if blank(r.get('address')) and blank(r.get('town')):
            rejected.append({'file': 'B', 'part': r.get('_part'), 'reason': 'no address and no town', 'row': json.dumps({k: s(v) for k, v in r.items()})[:800]})
            continue
        r['buyer_name_key'] = name_key(s(r.get('buyer')))
        r['seller_name_key'] = name_key(s(r.get('seller')))
        ak = addr_key(r.get('address'))
        is_port = ak.startswith('PORTFOLIO') or s(r.get('deal_type')).lower() == 'portfolio' and not re.match(r'^\d', ak)
        key = (ak, tk, y, r['buyer_name_key'] if is_port else '')
        groups[key].append(r)
    b_rows = []
    for k, rs in groups.items():
        vn = []
        for r in rs:
            vn.extend(r.get('_vnotes', []))
        m = merge_group(rs, B_COLS)
        for f in B_NUM:
            v, n = to_number(m.get(f), f)
            m[f] = v
            if n:
                vn.append(n)
        if blank(m.get('price_psf')) and isinstance(m.get('price'), (int, float)) and isinstance(m.get('sf'), (int, float)) and m['sf'] > 0 and s(m.get('deal_type')).lower() not in ('land',):
            m['price_psf'] = int(round(m['price'] / m['sf']))
            vn.append('psf computed')
        if isinstance(m.get('occupancy_at_sale'), (int, float)) and 0 < m['occupancy_at_sale'] <= 1:
            m['occupancy_at_sale'] = round(m['occupancy_at_sale'] * 100)
        if isinstance(m.get('cap_rate'), (int, float)) and 0 < m['cap_rate'] < 0.3:
            m['cap_rate'] = round(m['cap_rate'] * 100, 2)
        if vn:
            m['notes'] = (s(m.get('notes')) + ' | VALIDATION: ' + '; '.join(sorted(set(vn)))).strip(' |')
        apply_verification(m, ver.get('B', []), lambda r: name_key(s(r.get('address')) + ' ' + s(r.get('town'))))
        m.pop('_vnotes', None)
        b_rows.append(finish(m))
    b_rows.sort(key=lambda r: (s(r.get('date')), s(r.get('town')), s(r.get('address'))))
    write_csv(os.path.join(ROOT, 'deals_public_2019_2024.csv'), B_COLS, b_rows)
    report['B_rows'] = len(b_rows)
    report['B_portfolio_summary_rows'] = sum(1 for r in b_rows if s(r.get('address')).upper().startswith('PORTFOLIO'))
    report['B_by_year'] = dict(sorted(Counter(str(year_of(r.get('date')) or year_of(r.get('source_date')) or 'n/a') for r in b_rows).items()))
    report['B_by_county'] = dict(Counter(s(r.get('county')) or 'blank' for r in b_rows))
    report['B_with_price'] = sum(1 for r in b_rows if not blank(r.get('price')))
    report['B_with_sf'] = sum(1 for r in b_rows if not blank(r.get('sf')))
    report['B_with_cap_rate'] = sum(1 for r in b_rows if not blank(r.get('cap_rate')))
    report['B_with_spv'] = sum(1 for r in b_rows if not blank(r.get('buyer_spv_named')))

    # ---------------- C
    raw, bad = read_parts('C_entities')
    report['C_raw_rows'] = len(raw)
    report['C_unparseable_blocks'] = dict(bad)
    groups = defaultdict(list)
    for r in raw:
        if blank(r.get('entity_name')) or blank(r.get('buyer_name')):
            rejected.append({'file': 'C', 'part': r.get('_part'), 'reason': 'empty entity_name or buyer_name', 'row': json.dumps({k: s(v) for k, v in r.items()})[:800]})
            continue
        if not ok_url(r.get('evidence_url')):
            rejected.append({'file': 'C', 'part': r.get('_part'), 'reason': 'no valid evidence_url', 'row': json.dumps({k: s(v) for k, v in r.items()})[:800]})
            continue
        r['name_key'] = name_key(s(r.get('buyer_name')))
        r['entity_name_key'] = name_key(s(r.get('entity_name')))
        groups[(r['name_key'], r['entity_name_key'])].append(r)
    c_rows = []
    for k, rs in groups.items():
        m = merge_group(rs, C_COLS)
        apply_verification(m, ver.get('C', []), lambda r: r['entity_name_key'])
        c_rows.append(finish(m))
    c_rows.sort(key=lambda r: (r['name_key'], r['entity_name_key']))
    write_csv(os.path.join(ROOT, 'buyer_entities.csv'), C_COLS, c_rows)
    report['C_rows'] = len(c_rows)
    report['C_buyers_covered'] = len(set(r['name_key'] for r in c_rows))
    report['C_by_evidence_type'] = dict(Counter(s(r.get('evidence_type')) for r in c_rows))

    # ---------------- D
    raw, bad = read_parts('D_market')
    report['D_raw_rows'] = len(raw)
    report['D_unparseable_blocks'] = dict(bad)
    seen = set()
    d_rows = []
    for r in raw:
        if not ok_url(r.get('source_url')):
            rejected.append({'file': 'D', 'part': r.get('_part'), 'reason': 'no valid source_url', 'row': json.dumps({k: s(v) for k, v in r.items()})[:800]})
            continue
        v, n = to_number(r.get('value'), 'value')
        if blank(v):
            rejected.append({'file': 'D', 'part': r.get('_part'), 'reason': f'non-numeric value ({r.get("value")})', 'row': json.dumps({k: s(v2) for k, v2 in r.items()})[:800]})
            continue
        r['value'] = v
        yv, _ = to_number(r.get('year'), 'year')
        r['year'] = yv if not blank(yv) else s(r.get('year'))
        sd, n2 = norm_date(r.get('source_date'))
        r['source_date'] = sd
        key = (s(r['year']), s(r.get('quarter')), s(r.get('submarket')).lower(), s(r.get('size_band')).lower(), s(r.get('metric')).lower(), s(r.get('source_url')), s(v))
        if key in seen:
            continue
        seen.add(key)
        r['source_parts'] = r.get('_part', '')
        d_rows.append(r)
    d_rows.sort(key=lambda r: (s(r.get('year')), s(r.get('quarter')), s(r.get('submarket')), s(r.get('metric'))))
    write_csv(os.path.join(ROOT, 'market_buyer_mix.csv'), D_COLS, d_rows)
    report['D_rows'] = len(d_rows)
    report['D_by_metric'] = dict(Counter(s(r.get('metric')) for r in d_rows).most_common(40))
    report['D_by_year'] = dict(sorted(Counter(s(r.get('year')) for r in d_rows).items()))

    # ---------------- activity ranking (B deal counts + A nj_deal_count_seen + C entity counts)
    deal_counts = Counter()
    for r in b_rows:
        if r.get('buyer_name_key') and not s(r.get('address')).upper().startswith('PORTFOLIO'):
            deal_counts[r['buyer_name_key']] += 1
    a_by_key = {r['name_key']: r for r in a_rows}
    ent_counts = Counter(r['name_key'] for r in c_rows)
    keys = set(deal_counts) | set(a_by_key) | set(ent_counts)
    rank_rows = []
    for k in keys:
        a = a_by_key.get(k, {})
        seen_n = a.get('nj_deal_count_seen') if isinstance(a.get('nj_deal_count_seen'), (int, float)) else 0
        score = deal_counts.get(k, 0) * 2 + seen_n + (1 if a else 0)
        rank_rows.append({'name_key': k, 'buyer_name': a.get('buyer_name', ''), 'buyer_type': a.get('buyer_type', ''),
                          'in_buyers_stated': 'yes' if a else 'no', 'press_deal_rows_2019_2024': deal_counts.get(k, 0),
                          'nj_deal_count_seen_A': seen_n, 'entities_found': ent_counts.get(k, 0), 'activity_score': score})
    rank_rows.sort(key=lambda r: (-r['activity_score'], r['name_key']))
    write_csv(os.path.join(ROOT, 'buyer_activity_rank.csv'),
              ['name_key', 'buyer_name', 'buyer_type', 'in_buyers_stated', 'press_deal_rows_2019_2024', 'nj_deal_count_seen_A', 'entities_found', 'activity_score'], rank_rows)
    report['rank_rows'] = len(rank_rows)
    report['top_30_active'] = [(r['name_key'], r['activity_score'], r['press_deal_rows_2019_2024']) for r in rank_rows[:30]]
    report['buyers_in_B_not_in_A'] = [k for k, _ in deal_counts.most_common() if k not in a_by_key][:120]

    write_csv(os.path.join(ROOT, 'rejected_rows.csv'), ['file', 'part', 'reason', 'row'], rejected)
    report['rejected_rows'] = len(rejected)
    report['rejected_by_reason'] = dict(Counter(r['reason'].split(' (')[0] for r in rejected))
    with open(os.path.join(ROOT, 'consolidate_report.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=1, default=str)
    return report


if __name__ == '__main__':
    rep = consolidate()
    print(json.dumps({k: v for k, v in rep.items() if k not in ('buyers_in_B_not_in_A',)}, indent=1, default=str))
    print('buyers_in_B_not_in_A (first 60):', rep['buyers_in_B_not_in_A'][:60])
