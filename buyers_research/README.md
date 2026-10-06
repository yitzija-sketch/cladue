# buyers_research — NJ industrial buyer research (public-web arm)

Lead and buy-box research for a New Jersey industrial broker, meant to be **joined** to the broker's
local tax-roll / entity graph. Nothing here is investment advice, and nothing outside this folder was
modified (see `../NOTICE_buyers_research.md`). Status and how to continue: `RESUME.md`, `TURN_PLAN.md`,
`RESEARCH_LOG.md`. Raw agent output: `parts/`. Rebuild every CSV from the parts with
`python3 -I tools/consolidate.py`.

All CSVs are UTF-8, comma-separated, header row, one record per line. Blank = not found in a public free
source (never guessed). Numbers are plain (no `$`, `,`, `%`): `price` 18500000, `cap_rate` 5.75.
Dates are `YYYY-MM-DD`, `YYYY-MM` or `YYYY` depending on what the source gave.

## Join keys (helper columns, present in every file where a name appears)
`name_key`, `buyer_name_key`, `seller_name_key`, `entity_name_key` = name in UPPERCASE, punctuation
removed, tokens LLC / INC / LP / LLP / CORP / THE removed, `&` → `AND`, single-spaced.
Example: "The Hampshire Companies, LLC" → `HAMPSHIRE COMPANIES`.

## buyers_stated.csv (Workstream A)
| column | meaning |
|---|---|
| buyer_name, name_key, parent | buyer as named by sources; join key; parent/sponsor |
| buyer_type | REIT · open-end fund · closed-end PE · family office · developer-holder · owner-user · IOS specialist · other |
| hq_address, hq_city, hq_state, nj_office_address, website | identity |
| min_sf, max_sf, min_price, max_price | **stated** size/price range (blank if the buyer publishes none) |
| building_age_pref, clear_height_pref, product_types, target_submarkets | stated preferences (text) |
| tenancy_pref | vacant · stabilized · either |
| hold_strategy | core · core-plus · value-add · opportunistic · merchant-build |
| equity_source, deal_structures | e.g. open-end fund / all-cash, JV, sale-leaseback, portfolio, 1031 |
| stated_criteria_quote | verbatim ≤20 words from criteria_source_url |
| criteria_source_url, criteria_date | where/when the stated criteria were published |
| acquisitions_head_name, acquisitions_head_title, work_email_or_pattern, phone, linkedin | only when seen publicly; emails as `pattern: …` only if a real address at that domain was seen |
| confidence | high (filing / named person quoted) · med (marketing page, trade press) · low (inferred — inferred traits live in `notes` prefixed INFERRED:) |
| nj_active, nj_deal_count_seen | yes/no/unknown; number of distinct NJ industrial buys 2019–26 the researcher saw (not exhaustive) |
| source_url | criteria_source_url, or best URL evidencing NJ activity (never blank) |
| notes, verification, source_parts, dupes_merged | free text; verification tags from the skeptic pass; which part files contributed |

## deals_public_2019_2024.csv (Workstream B)
| column | meaning |
|---|---|
| date, source_date | sale/announcement date; article date |
| address, town, county | property (county filled from town; only the 11 in-scope counties) |
| buyer, buyer_name_key, buyer_parent, buyer_spv_named | buyer; sponsor; the LLC/fund named in the source if any |
| seller, seller_name_key, seller_parent | seller side |
| sf, acres, price, price_psf, cap_rate | numeric; price_psf computed when both price and sf were stated ("psf computed" in notes) |
| property_type | industrial · warehouse · flex · IOS · truck terminal · cold storage · small-bay · land · other |
| year_built, occupancy_at_sale (percent), tenant, lender, loan_amount | when stated |
| brokers | "Listing: Firm (names); Procuring: Firm (names)" or firm(s) |
| deal_type | sale · sale-leaseback · portfolio · land · JV · ground lease |
| portfolio_context | e.g. "part of 4-building, 256,000 SF, $XXM Carlstadt/East Rutherford portfolio"; summary rows have address `PORTFOLIO: n buildings` |
| source_url, confidence, notes, verification, source_parts, dupes_merged | as above |

## buyer_entities.csv (Workstream C)
| column | meaning |
|---|---|
| buyer_name, name_key | sponsor the entity belongs to |
| entity_name, entity_name_key | legal entity verbatim; join key |
| entity_role | SPV · GP · manager · fund · affiliate · former name |
| state_of_formation, mailing_or_registered_address, signatory_or_officer_names | when stated |
| evidence_type | 10-K Schedule III · 10-K Ex.21 · Form D · Form ADV · 8-K/loan doc · UCC · deed recital · press · loan press · NJ/DE filing · municipal record · permit · ownership note |
| evidence_url, confidence, notes, verification, source_parts, dupes_merged | as above; notes carry the NJ property the SPV holds when known |

## market_buyer_mix.csv (Workstream D)
| column | meaning |
|---|---|
| year, quarter | Q1–Q4 · H1/H2 · FY · blank |
| submarket | Northern NJ · Central NJ · New Jersey · Meadowlands · Port · Exit 8A … |
| size_band | <50K · 50-100K · 100-250K · 250-500K · 500K+ · all (or the report's own band) |
| metric | e.g. sales_volume, avg_price_psf, cap_rate(_low/_high), buyer_share_institutional/private/user/foreign/reit, top_buyer_mention, vacancy_rate, asking_rent_psf, net_absorption_sf, land_value_per_acre, trend_statement |
| value, unit | number; USD · USD_millions · USD/SF · USD/acre · percent · SF · SF_millions · count · rank · bps |
| source_name, source_url, source_date, notes, source_parts | report title, URL, date; context (class, trailing-12-month, etc.) |

## Helper outputs
* `buyer_activity_rank.csv` — name_key, buyer_name, buyer_type, in_buyers_stated, press_deal_rows_2019_2024,
  nj_deal_count_seen_A, entities_found, activity_score (= 2×press deals + A deal count + 1 if in A). Used to pick C/E targets.
* `rejected_rows.csv` — rows dropped by validation and why (no source_url, out of window/scope, no address+town, non-numeric value).
* `consolidate_report.json` — counts by file/year/county/type, top-30 active, buyers seen in B but missing from A.
* `dossier_<buyer>.md` — Workstream E one-pagers (written after C/verification).

## Provenance and limits
Round 1 (2026-10-06) was search-excerpt based only: this environment blocked page fetches, and WebSearch
was capped at 200 calls per turn, so coverage after round 1 is partial (see `RESEARCH_LOG.md` §2–3). Each
row's `source_url` was present in the researcher's search results; the verification pass (`parts/V_verify`)
re-checks samples and tags rows `confirmed` / `refuted` / `unverifiable` in the `verification` column.
