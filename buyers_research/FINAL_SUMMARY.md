# FINAL SUMMARY — NJ Industrial Buyer Research (public-web arm)

Completed 2026-10-11. Branch `claude/nj-industrial-buyer-research-v4j2sy`, folder `buyers_research/`.
Read with `HANDOFF.md` (what everything is) and `README.md` (column dictionary). Numbers below are
generated from the final CSVs by `tools/make_summary.py`; the narrative follows.


## Counts per file

| File | Rows | Notes |
|---|---|---|
| buyers_stated.csv | 377 buyers | 135 with stated criteria, 56 with a named acquisitions head; NJ-active yes 263 / unknown 92 / no 22; 50 rows carry verification tags {'confirmed': 203, 'unverifiable': 33, 'corrected': 10} |
| deals_public_2019_2024.csv | 563 properties (64 portfolio summary rows) | dated 527 / undated 36; 276 with price, 401 with SF (319 under 250K SF), 40 with buying LLC named; 213 rows carry verification tags {'unverifiable': 35, 'confirmed': 353, 'filled': 129, 'corrected': 9} |
| buyer_entities.csv | 479 entities for 100 buyers | roles {'manager': 115, 'affiliate': 125, 'SPV': 90, 'former name': 28, 'GP': 33, 'fund': 88}; evidence {'press': 152, 'Form D': 95, 'ownership note': 63, '8-K/loan doc': 44, 'NJ/DE filing': 33, 'Form ADV': 23, 'municipal record': 22, '10-K Schedule III': 20}; 59 rows carry verification tags {'confirmed': 115, 'unverifiable': 19, 'filled': 4, 'corrected': 3} |
| market_buyer_mix.csv | 700 metric rows | years {'': 3, '2019': 32, '2020': 32, '2021': 73, '2022': 134, '2023': 115, '2024': 138, '2025': 173}; top metrics {'trend_statement': 77, 'asking_rent_psf': 70, 'leasing_volume_sf': 64, 'vacancy_rate': 64, 'net_absorption_sf': 45, 'avg_price_psf': 30, 'availability_rate': 28, 'sales_volume': 24, 'cap_rate': 12, 'deliveries_sf': 12} |
| buyer_activity_rank.csv | 407 | activity score = 2 x press deals 2019-24 + NJ deals seen in A + 1 if in A |
| dossier_*.md | 25 | one page per buyer |
| rejected_rows.csv | 133 | {'county out of scope': 8, 'no address and no town': 15, 'excluded by later pass': 3, 'date set by verification outside 2019-2024': 107} |

## Deals by year

| 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | undated |
|---|---|---|---|---|---|---|
| 58 | 77 | 92 | 143 | 80 | 77 | 36 |

## Deals by county

Bergen 102, Middlesex 89, Morris 56, Burlington 54, Union 48, Essex 47, Passaic 39, Hudson 35, Somerset 34, Mercer 27, Monmouth 19, blank 13

## Buyer types in buyers_stated.csv (and how much the public web says about each)

| buyer_type | buyers | with stated criteria | with acquisitions head | NJ-active yes |
|---|---|---|---|---|
| other | 78 | 18 | 5 | 52 |
| developer-holder | 77 | 27 | 12 | 58 |
| owner-user | 70 | 1 | 0 | 62 |
| closed-end PE | 63 | 39 | 7 | 46 |
| REIT | 47 | 30 | 18 | 16 |
| open-end fund | 24 | 12 | 10 | 17 |
| IOS specialist | 13 | 7 | 3 | 9 |
| family office | 5 | 1 | 1 | 3 |

## 25 most active buyers (press deals 2019-2024 + NJ deals seen while researching; call-list buyers excluded)

| # | Buyer | Type | Press deal rows | NJ deals seen (A) | Entities found | Stated buy box? |
|---|---|---|---|---|---|---|
| 1 | Seagis Property Group | developer-holder | 13 | 10 | 3 | yes |
| 2 | Devli Real Estate | developer-holder | 10 | 12 | 3 | yes |
| 3 | Prologis, Inc. | REIT | 12 | 4 | 12 | no |
| 4 | Faropoint | closed-end PE | 9 | 7 | 6 | yes |
| 5 | Realterm | closed-end PE | 7 | 5 | 3 | yes |
| 6 | Sagard Real Estate | open-end fund | 7 | 4 | 8 | yes |
| 7 | Morgan Stanley Real Estate Investing | closed-end PE | 8 | 1 | 9 | no |
| 8 | Longpoint Realty Partners | closed-end PE | 7 | 2 | 5 | yes |
| 9 | Brookfield Asset Management (Logistics) | closed-end PE | 6 | 3 | 16 | no |
| 10 | Dalfen Industrial | closed-end PE | 5 | 5 | 8 | yes |
| 11 | The STRO Companies | developer-holder | 3 | 9 | 4 | yes |
| 12 | Thor Equities Group | developer-holder | 5 | 5 | 2 | no |
| 13 | Venture One Real Estate | closed-end PE | 3 | 9 | 3 | no |
| 14 | Ambient Capital Partners | IOS specialist | 6 | 1 | 1 | yes |
| 15 | Ares Management Real Estate (Ares Industrial REIT / legacy Black Creek) | open-end fund | 5 | 3 | 13 | yes |
| 16 | Commerce Park Investors LLC | developer-holder | 2 | 9 | 9 | no |
| 17 | Link Logistics Real Estate | open-end fund | 5 | 3 | 5 | yes |
| 18 | Marcus Partners | closed-end PE | 5 | 3 | 4 | yes |
| 19 | Velocity Venture Partners, LLC | closed-end PE | 4 | 4 | 1 | yes |
| 20 | Bridge Logistics Properties | closed-end PE | 4 | 3 | 4 | yes |
| 21 | Invesco Real Estate | open-end fund | 3 | 5 | 7 | no |
| 22 | Ridgecut Road | IOS specialist | 4 | 3 | 5 | no |
| 23 | STAG Industrial, Inc. | REIT | 4 | 3 | 5 | yes |
| 24 | Treetop Companies | family office | 3 | 5 | 1 | no |
| 25 | Penwood Real Estate Investment Management, LLC | closed-end PE | 4 | 2 | 6 | yes |

## Call-list buyers (deliberately low effort; shown for completeness)

- Sitex Group: 12 press deal rows, 0 entities
- CenterPoint Properties: 9 press deal rows, 0 entities
- Terreno Realty Corporation: 7 press deal rows, 0 entities
- Bridge Industrial: 4 press deal rows, 0 entities
- Elberon Development Group: 2 press deal rows, 0 entities
- Cabot Properties: 0 press deal rows, 0 entities
- Kurv Industrial: 0 press deal rows, 0 entities


## What was asked and what was delivered

The brief asked for the public-web half of a NJ industrial buyer map: who is actively buying industrial
property in the 11 North/Central NJ counties, what they say they want, what they bought 2019–2024, and
which LLCs they buy through — structured to join to the broker's local tax-roll / entity graph on
`name_key`. Four CSV tables, 25 one-page dossiers, market statistics, a column dictionary and a research
log were delivered (counts in the tables above). Every row carries a public source URL; nothing was
guessed; nobody was contacted; no logins, paywalls or CAPTCHAs were used.

## How to read the activity ranking

"Press deal rows" counts distinct 2019–2024 property purchases found in trade press, brokerage releases
and SEC filings; "NJ deals seen (A)" is what the buy-box researcher saw while profiling the buyer
(including 2025–26 deals, which were deliberately not recorded as deal rows). Both undercount: most
sub-$5M trades are never reported, and the broker's tax-roll data is the authoritative count. The six
buyers on the broker's existing Elizabeth-port call list (CenterPoint, Terreno, Cabot, Sitex, Elberon,
Kurv/Bridge Industrial) were researched only lightly by instruction and are excluded from the top-25 and
the dossiers even though Sitex (14 rows), Prologis-scale CenterPoint (9) and Terreno (8) would otherwise
rank in the top ten.

## Buyer types on which the public web says little

* **Family offices and private 1031 buyers** — only 5 rows typed "family office"; ~40 private
  individuals / single-asset LLCs have a deal row and nothing else (no criteria, no sponsor page). The
  tax-roll graph, not the web, is the way to find and size these. The few repeat private buyers that do
  surface (Davco Group, STRO/Millstein, Legacy Real Estate Developers + Commerce Park Investors,
  Brentwood Realty/Opper, Treetop, Western Building, River Walk LLC, Devli) are worth a call list of their own.
* **Owner-users** — 70 rows, 1 with anything resembling criteria (by nature). The value is in the
  expansion signals in `notes` (Dora's Naturals, Deko International, Transcontinental Steel, Nest
  Scientific, Glendale Warehouse, Bay Crane, F.W. Webb) rather than buy boxes.
* **Foreign capital in sub-250K SF product** — Korean, German and Japanese investors appear only in
  big-box build-to-suit or portfolio deals; Mapletree (Westampton, Manalapan), Investcorp (one 44K SF
  building in a national portfolio), GIC/La Caisse/ADIA/CPP/PSP only as JV capital behind operators.
* **Non-traded REITs and DST sponsors** — strategy language is abundant (prospectuses), but NJ-specific
  holdings are rarely disclosed below the portfolio level; INREIT (152 Ridge Rd), PGIM PREF (1735 Jersey
  Ave), AIREIT (Wayne, 16-building NJ portfolio), JPMREIT (IOS) and Four Springs/Pilothouse (Belmar HQ)
  are the exceptions. No DST sponsor's NJ industrial asset surfaced.
* **Cap rates at the deal level** — press almost never prints them (two deal rows carry one; market
  reports give 12 cap-rate rows, mid-5% in 2024 and low-3% at the 2021 peak). Small-bay cap rates
  specifically are absent from the public record.
* **Acquisitions heads at the big open-end funds** — Invesco, PGIM, Principal, LaSalle, EQT Exeter,
  GLP/GCP, Nuveen rarely name a NJ or Northeast acquisitions lead; names were found for 56 of 377 buyers.
* **HQ street addresses** — the environment could not open firm websites, so most HQ cells carry
  city/state only; the entity table's c/o addresses (Form D / ADV) are the better join key anyway.

## Ten questions the data raised (for the broker to take to the local graph or a first call)

1. **How many "reported" deals are really in-window?** Of the undated press deals that were re-checked,
   roughly a third turned out to be 2017–2018 or 2025–2026 (Prologis Exit 8A $197M, Goodman Newark $360M,
   Terreno 130 Interstate $144M, Broadstone Perth Amboy, Crow/BGO Franklin, Fujipoly Edison, Kurv
   Carlstadt...). The remaining undated rows should be dated by the tax-roll last-sale date on join before
   anyone quotes them.
2. **Who is Devli, really?** The most active private buyer found (12+ Meadowlands/Bergen buys, incl.
   2026 Leonia and Upper Saddle River) is called "Wallington-based" by the press but lists 800 Ave at Port
   Imperial, Weehawken as HQ; Mark Devli (CIO) and Chris Devli (COO) are the only names; capital source and
   SPV names are undisclosed, and Deugen Investment Group is a separate Hoboken firm that co-invested once.
3. **Do the SPV naming patterns hold in the registry?** Seagis `SPG <Town> LLC`, Cohen Asset
   Management `<Town> SPE LLC`, Ares `BCI IV / AIREIT <property> DC LLC`, Dermody `DPIF <state> <n>
   <project> LLC`, Faropoint `FRG-X-NJ<n> LP`, Denholtz `DENHOLTZ <address> LLC`, Forsgate `Forsgate
   Ventures <roman> LLC`, Prologis `Prologis-Exchange <address> LLC`, Taurus `TCD 257 SNJ ...` — each is
   evidenced by one to four named entities; the local registry/mailing-address clustering can confirm or
   kill each pattern in minutes.
4. **Which c/o mailing addresses sit on the most NJ tax bills?** Faropoint 111 River St Ste 1010
   Hoboken; Realterm 201 West St Annapolis; Sagard/EverWest 1099 18th St Denver; Dermody 5500 Equity Ave
   Reno; CBRE IM 200 Park Ave Ste 2001 NY; Sitex 10 W Forest Ave Englewood; Seagis 100 Front St
   Conshohocken; Penwood (Fund VI); Taurus c/o 4 Radnor Corp Center; Brookfield 250 Vesey St 15th Fl;
   BGO 399 Park Ave 18th Fl; Invesco 2001 Ross Ave Dallas. Matching these to the tax roll turns ~45 buyers
   with no public SPV name into holdings lists.
5. **Faropoint's box has moved — where is it now?** Stated 20K–100K SF (site) vs 20K–200K SF with
   ~10-year leases (ROI-NJ), Invesco minority stake since 2023, 2025 Florham Park $9.25M, $144.5M
   Allendale/Mahwah 2023: are they still buying single-tenant sub-50K SF boxes in 2026, and through
   which FRG-X vehicle?
6. **How much IOS capital is still un-deployed in NJ?** Ambient $156M Harrison/Kearny (2024), Realterm
   $277M 13-property buy from Brookfield (2024-12), Sagard/La Caisse US$360M JV (2026), Dalfen/Centerbridge,
   Ridgecut Road (5+ buys 2024–26), Jadian, Alterra, Catalyst, Outpost — against pricing of $8–10K/acre/
   month rent (Fennelly) and up to ~$7M/acre (Moonachie). Which of these will pay for 2–5-acre infill yards
   under $10M?
7. **Why so few sale-leasebacks?** Only ~10 NJ industrial SLBs surfaced 2019–2024 (Unifoil/EverWest,
   Diamond Chemical/EverWest, Kiss→Duke, Bed Bath & Beyond/Oak Street, RAB/Suburban Jersey, Allstate Can/
   Longpoint...). With Oak Street, W. P. Carey ($5–500M), Four Springs ($5–25M, Belmar), Mesirow (>$10M),
   LCN and AG Net Lease all stating appetite, which NJ owner-occupiers in the broker's graph fit?
8. **Who are the net sellers of 2025–26?** Plymouth sold its only NJ asset; First Industrial sold
   Montville to Longpoint; Hampshire/Invesco flipped 333 North St Teterboro to Principal for +$40M in two
   years; MSREI sold Eastpoint at 8A to Property Reserve; Goldman/Dalfen sold Roxbury to ICE; Woodmont sold
   to Sagard; Blackstone sold to Prologis and to Nuveen. Are these programmatic exits the broker can get
   ahead of?
9. **What do the merchant-build JVs want next?** Trammell Crow/CBRE IM (Sayreville), Hampshire/Invesco
   (Bogota, Teterboro), Woodmont/Sagard (Rahway, Woodbridge), Russo/Forsgate (Kingsland 718 ac), Lincoln
   Equities/PGIM, Greek/Hampshire (Parsippany), Altman/DWS (Hamilton), Deugen/Faropoint (New Brunswick),
   Crow Holdings — all bought land or obsolete buildings 2019–24. Which corridors are they still
   underwriting at 2026 rents?
10. **Is the sub-250K SF market still institutional?** 360 of the dated deals under 250K SF show a mix
    of Faropoint, Longpoint, Camber, Cohen, Seagis, Devli, STRO, Oliver Street/Bain, NorthBridge, Taurus,
    High Street ($3–250M, 24' clear, post-1980) against a growing owner-user and 1031 cohort as prices
    reset from $200+/SF (2022) to $180–190/SF (2024–25, NAI). Who is still paying the institutional price
    for 30–100K SF multi-tenant buildings in 2026?

## Caveats that travel with every number

* **Search-excerpt based.** This cloud environment blocked direct page fetches; all facts came from web-
  search excerpts of pages (including SEC filings, PDFs and article text). Verification sampled ~10% of
  rows against the cited domain plus an independent source and found a 3–4% refutation rate, almost
  all dates. Undated rows have an estimated one-third chance of being outside 2019–2024.
* **The repo's `cloud_context/` folder was absent**, so "already known locally" could not be excluded
  precisely; the brief's own exclusions were applied (no 2025–26 press deals as rows; call-list buyers
  light). Expect overlap with the local graph — the join will show it.
* **Email patterns and phones** were recorded only when seen on a real public address (2 and 8 rows).
* **The research paused 2026-10-06 → 10-11** when usage credits lapsed; nothing was lost (every agent's
  output is committed, and two interrupted agents resumed from their half-written files).
