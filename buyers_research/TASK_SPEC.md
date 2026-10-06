# TASK_SPEC — original brief (verbatim essentials) for the NJ industrial buyer research

## Setup note
The repo was expected to contain `cloud_context/` (names/URLs of what the local build already has, incl.
`known_buyers_already_in_local_graph.csv`). **It was not present on any branch.** Fallback: apply the
exclusions below from the brief itself. Write all output to `buyers_research/` and commit it.

## Role and goal
Public-web research arm of a New Jersey industrial tenant-rep / investment-sales broker. A local build on
the broker's PC already links NJ tax-roll owners (LLCs) into holding groups (mailing addresses, registry
IDs, people, phones, emails, SEC filings) and derives each group's revealed buy box from actual sales.
Do NOT recreate that. Job: who the active buyers/funds of NJ industrial property are, what they say they
want, what they have actually bought, and the shell entities they buy through. Output is joined to the
local graph later — structure over prose.

## Scope
* Geography: Bergen, Burlington, Essex, Hudson, Mercer, Middlesex, Monmouth, Morris, Passaic, Somerset,
  Union counties (NJ); a buyer's NJ activity only (other markets only if they show strategy).
* Property: industrial, warehouse, flex, IOS, truck terminals, cold storage, small-bay/multi-tenant
  industrial, industrial land. Focus on buildings under ~250,000 SF; record bigger buyers too.
* Time: acquisitions 2019–today for deal history; current stated criteria for buy boxes.

## Already done locally — do NOT redo
* Tax-roll last-sale/owner data (288K parcels), mailing-address clustering, NJ business registry unmasking,
  county clerk deed reads (Essex/Union/Hudson/Passaic partial).
* SEC EDGAR sweep: 10-K Exhibit 21 subsidiaries and Form D filings matched to NJ owners.
* 404 trade-press deals dated 2025–2026 (re-nj.com, ROI-NJ, NJBIZ, etc.).
* Broker call list for buyers of 600K SF Elizabeth port product (CenterPoint, Terreno, Cabot, Sitex,
  Elberon, Kurv…) — do not spend effort; only add NEW facts when re-encountered.

## Workstreams (parallel subagents, own output file each)
**A. Stated buy boxes — `buyers_stated.csv`** (target 150+ buyers; REITs, institutional/open-end, PE/
value-add, 1031/PE roll-ups, family offices, repeat owner-operators, IOS/truck-parking, cold-storage/
last-mile, NJ developer-holders). Seed list in `tools/workflows/nj-buyers-a.js`. Columns: buyer_name,
parent, buyer_type (REIT|open-end fund|closed-end PE|family office|developer-holder|owner-user|IOS
specialist|other), hq_address, hq_city, hq_state, nj_office_address, website, min_sf, max_sf, min_price,
max_price, building_age_pref, clear_height_pref, product_types, target_submarkets, tenancy_pref
(vacant|stabilized|either), hold_strategy (core|value-add|opportunistic|merchant-build), equity_source,
deal_structures (all-cash|JV|sale-leaseback|portfolio|1031), stated_criteria_quote (≤20 words),
criteria_source_url, criteria_date, acquisitions_head_name, acquisitions_head_title,
work_email_or_pattern, phone, linkedin, confidence (high|med|low), notes. Sources: fund "acquisition/
investment criteria" pages, REIT decks/supplementals, broker buyer-criteria pages, LoopNet/CREXi/CoStar
press, conference bios, SEC ADV public pages, press quotes.

**B. Historic acquisitions 2019–2024 — `deals_public_2019_2024.csv`** from press/market reports the local
2025–26 file lacks (acquisition announcements, "sells for $X", broker deal-closed releases from Cushman,
CBRE, JLL, Colliers, NAI, Newmark, Avison Young, Kislak, SVN, Lee & Associates, Marcus & Millichap,
Savills, Meridian; REIT quarterly acquisition lists; NJ Business/ROI-NJ/Real Estate NJ/Commercial
Observer/Bisnow/GlobeSt/The Real Deal archives). Columns: date, address, town, county, buyer,
buyer_parent, buyer_spv_named, seller, seller_parent, sf, acres, price, price_psf, cap_rate,
property_type, year_built, occupancy_at_sale, tenant, lender, loan_amount, brokers, deal_type
(sale|sale-leaseback|portfolio|land|JV|ground lease), portfolio_context, source_url, source_date,
confidence. One row per property; portfolios: one row per listed address plus a summary row.

**C. Shell-entity and address discovery — `buyer_entities.csv`** for each buyer in A (priority: 100 most
active). Columns: buyer_name, entity_name, entity_role (SPV|GP|manager|affiliate|former name),
state_of_formation, mailing_or_registered_address, signatory_or_officer_names, evidence_type (10-K
Schedule III|10-K Ex.21|Form D|Form ADV|UCC|deed recital|press|NJ/DE filing|permit|ownership note),
evidence_url, confidence. Method: REIT 10-K Schedule III lists and subsidiary exhibits for NJ addresses,
naming-pattern analysis, "an affiliate of" stories, Form ADV Schedule D fund names, lender/loan press,
NJ DOS / Delaware listings only if freely viewable.

**D. Market-level buyer statistics — `market_buyer_mix.csv`** from free quarterly/annual reports (C&W,
CBRE, JLL, Colliers, Newmark, Avison Young, NAI Hanson, Kislak, Lee & Associates, Savills, CoStar free
summaries, RCA articles) for North/Central NJ and Meadowlands/Port/I-95/I-78/Route 1: buyer share by type
(institutional, private, user, foreign), avg $/SF by size band, cap-rate ranges by size band, volume by
year, trends (IOS, last-mile, cold storage). Columns: year, quarter, submarket, size_band, metric, value,
unit, source_name, source_url, source_date, notes.

**E. Dossiers** — for the 25 most active buyers from A, one-page `dossier_<buyer>.md`: strategy, last
5–10 NJ acquisitions (from B/C), typical check size, entities used, key people, what makes a property
match them, and 5 open questions for a first call.

## Rules
1. Public free web only. No logins, accounts, CAPTCHAs, paywalls, ToS-violating scraping. Prefer official
   sources over aggregators.
2. Every row needs `source_url`. Unsourced → blank; never guess; never invent people/emails/phones. Email
   patterns labelled `pattern`, only when seen on a real address at that domain.
3. `confidence`: marketing page = med; named person quoted = high; inferred from deals = low (notes only).
4. Dedupe one row per buyer/entity/property; helper `name_key` (UPPERCASE, no punctuation, strip
   LLC/INC/LP/CORP/the) for joining.
5. No investment advice. 6. Never contact anyone or submit anything.
7. Parallel subagents (A by buyer type; B by year and publication; C by buyer; D by brokerage); each
   writes its own part; final step concatenates, dedupes, validates (no empty source_url, dates parse,
   SF/price numeric).

## Deliverables (in `buyers_research/`)
`buyers_stated.csv`, `deals_public_2019_2024.csv`, `buyer_entities.csv`, `market_buyer_mix.csv`,
`dossier_*.md`, `RESEARCH_LOG.md` (what was searched, blocked, not found, counts per file), `README.md`
(column dictionary). Finish with a summary: counts per file, the 20 most active buyers, buyer types with
little found, top 10 questions the data raised.

## Standing instructions from the broker during the run
* Record all progress continuously (commit + push) so a credit lapse loses nothing; include background
  agents/tasks in the record.
* Do not modify the broker's existing files/database in the repo; keep everything inside
  `buyers_research/` and leave a notice of what was added (`NOTICE_buyers_research.md`).
