# RESEARCH_LOG — NJ industrial buyer research (public-web arm)

Status: **COMPLETE** (2026-10-11 08:50Z). Session: https://claude.ai/code/session_0126gXTSDEH4CeHTDhskFo5J
Branch `claude/nj-industrial-buyer-research-v4j2sy`, folder `buyers_research/`. Rebuild all CSVs from the raw
parts at any time with `python3 -I buyers_research/tools/consolidate.py`.

## 0. Setup findings

* `cloud_context/` **was not present in the repository** on any branch, so
  `known_buyers_already_in_local_graph.csv` could not be used. Fallback: the exclusions in the task text
  were applied (no 2025–2026 press deals recorded as deal rows; minimal effort on the Elizabeth-port call
  list — CenterPoint, Terreno, Cabot, Sitex, Elberon, Kurv/Bridge). Deal history was collected from press,
  not tax records, so nothing here duplicates the local tax-roll work; overlap with local *knowledge* is
  likely and the `name_key` join will show it.
* **Network policy** blocked every direct page fetch (WebFetch/curl → `EGRESS_BLOCKED` for re-nj.com,
  sec.gov, efts/data.sec.gov, rebusinessonline.com, fund sites). WebSearch worked and returns page excerpts
  (incl. SEC filings and PDFs), so all research is search-derived and a verification pass re-searched the
  important claims. **WebSearch is capped at 200 calls per turn shared by all agents**; the work therefore
  ran as 14 batches of ≤7–16 agents with hard per-agent caps, one batch per turn (turns were created by
  self-scheduled wake-ups), each batch committed before the next.
* No logins, forms, CAPTCHAs or paywalls were used. Nobody was contacted. No file outside
  `buyers_research/` and `NOTICE_buyers_research.md` was touched.

## 1. Method

~120 research/verification agents (Workflow tool), each writing one JSONL part file under `parts/`, then
`tools/consolidate.py`: normalises numbers/dates, fills county from town, applies the alias table
(`parts/_runs/ALIASES.json`) and exclusion list (`parts/_runs/EXCLUDE_B.jsonl`), dedupes (buyer by
`name_key`; property by address+town+year; entity by buyer+entity key) keeping the most complete row and
highest confidence, applies verification verdicts (`parts/V_verify/`), rejects rows without a source URL
or outside scope/window, computes $/SF, and writes the CSVs, `buyer_activity_rank.csv`,
`rejected_rows.csv` and `consolidate_report.json`.

| Batch | Agents | Searches | Output |
|---|---|---|---|
| 1 (10-06) A buyer-type groups A1–A9, round 1 + re-run | 9 + 7 | ~200 + 190 | 9 part files, 256 buyers |
| 2–3 B year sweeps 2019–2024; 6 county-cluster sweeps | 6 + 6 | 185 + 168 | ~820 raw deal rows |
| 4 B REIT-disclosure slices; D brokerage groups 3–6 | 2 + 4 | 180 | 45 deal rows; 319 metric rows |
| 5 A expansion (deal buyers without buyer rows: institutional / owner-users / private LLCs); A1–A2, D1–D2 top-ups | 7 | ~170 | +130 buyers; D to ~750 raw rows |
| 6–9 C entities, 20 batches × 5 buyers (10-06 → 10-11, credit lapse in between) | 20 | ~640 | 492 raw entity rows |
| 10 V skeptics: 10 A files + 6 B files × 6 rows | 16 | 192 | ~500 verdicts |
| 11 V skeptics: 8 C files; dating pass on 55 undated ≥$5M deals; IOS/cold + SLB/land specialty sweeps | 12 | 190 | ~250 verdicts; 43 specialty rows |
| 12 E dossiers, 25 buyers | 25 | 175 | 25 dossiers (~29K words) |
| 12b second dating pass, 148 undated rows | 5 | 150 | 148 date verdicts |
| 13 final consolidation, summary, docs | 0 | 0 | this file, FINAL_SUMMARY.md |

## 2. What was searched, what was blocked, what could not be found

**Searched (≈2,300 WebSearch calls in total):** trade press (roi-nj.com, re-nj.com incl. monthly
flipbooks, njbiz.com, njbmagazine, Commercial Observer, GlobeSt, The Real Deal, Bisnow, REBusinessOnline,
Connect CRE, CoStar News, traded.co, Jersey Digs, Meadowlands Media); brokerage newsrooms (C&W, CBRE, JLL,
Colliers, Newmark, Avison Young, NAI Hanson, NAI DiLeo-Bram, NAI Mertz, Kislak, Lee & Associates, M&M, SVN,
Savills, Bussel, Resource Realty, Zimmel, Team Resources, Fennelly); wires (PRNewswire, BusinessWire,
GlobeNewswire); sec.gov (10-K Schedule III, 8-K, Form D, Form ADV/IAPD, S-11, DEF 14A); fund and REIT
websites (acquisition-criteria/strategy/team pages); municipal records (planning-board agendas and
resolutions, PILOT ordinances, NJSEA notices, tax-appeal decisions); registry mirrors (OpenCorporates,
Bizapedia, LEI records, FL Sunbiz, NY DOS) only where excerpts were freely visible.

**Blocked:** all direct page fetches (network policy); WebSearch beyond 200 calls/turn (worked around by
batching); EDGAR full-text search and NJ DORES business search are not reachable through search excerpts;
property-record aggregators (njpropertyrecords, PropertyShark, NJParcels) mask grantee names in excerpts.

**Not found / thin (see FINAL_SUMMARY.md for the full list):** property-level SPV names for ~45 of the
100 buyers (only c/o mailing addresses or naming patterns found); HQ street addresses for most buyers;
acquisitions heads at most open-end funds; deal-level cap rates (2 deal rows; 12 market rows); DST
sponsors' NJ industrial holdings; family-office and 1031 buyers beyond their single deal row; cold-storage
building sales 2019–2024 beyond Hall's/Americold, Preferred Freezer/Lineage, Provender Delanco and
CenterPoint 200 Polar Way; IOS sales in 2019–2020; brokerage newsroom coverage for Colliers, Newmark,
Avison Young, Kislak, M&M (few dated NJ sale releases surface in search).

## 3. Counts per file (final)

| File | Rows | Notes |
|---|---|---|
| buyers_stated.csv | 377 buyers | 135 with stated criteria; 56 with named acquisitions head; NJ-active 263 yes / 92 unknown / 22 no; 50 verification-tagged (203 confirmed, 10 corrected, 33 unverifiable) |
| deals_public_2019_2024.csv | 563 properties (64 portfolio summaries) | 527 dated / 36 undated; 276 with price; 401 with SF (319 < 250K SF); 40 with buying LLC named; 213 verification-tagged (353 confirmed, 129 blank fields filled, 9 corrected, 35 unverifiable) |
| buyer_entities.csv | 479 entities / 100 buyers | 90 SPV, 88 fund, 33 GP, 115 manager, 125 affiliate, 28 former name; evidence: press 152, Form D 95, 8-K/loan 44, NJ/DE filing 33, Form ADV 23, municipal 22, 10-K 30; 59 verification-tagged |
| market_buyer_mix.csv | 700 metric rows | 2019–2025; vacancy 64, asking rent 70, leasing 64, absorption 45, $/SF 30, sales volume 24, cap rate 12, IOS $/acre 4+, trend statements 77 |
| buyer_activity_rank.csv | 407 | helper ranking |
| dossier_*.md | 25 | one page each |
| rejected_rows.csv | 133 | 107 dated outside 2019–2024 by verification; 15 no address/town; 8 out-of-scope county; 3 manual exclusions |
| parts/V_verify | 787 verdict lines | 32 skeptic agents |

## 4. Checkpoint notes

* 10-06 18:15Z — workflows A/B/D launched (29 agents); discovered the 200-searches-per-turn cap; re-planned
  into batches (`TURN_PLAN.md`); scripts made budget-aware (per-agent caps, append-to-file, carry-forward
  leads via `parts/_runs/LEADS.json`); auto-checkpoint loop (`tools/checkpoint.sh`) committing every 10 min.
* 10-06 19:00–20:30Z — batches 1–5 (buyers 377, deals ~820 raw, market ~750 raw); alias table added
  (variants/former names → one buyer); batch 6 (entities 1–25) started.
* 10-06 20:30Z — **usage credits lapsed**; two entity agents died after half-way writes; everything committed.
* 10-11 06:00Z — **resumed**; C_02/C_05 resumed from their partial files; batches 7–9 (entities 26–100).
* 10-11 07:05–07:45Z — batch 10–11 verification: 16 + 8 skeptics, first dating pass, specialty sweeps;
  consolidator extended to apply verdicts, normalise corrected values, fill blanks from confirmed findings
  and drop rows whose verified date falls outside 2019–2024.
* 10-11 07:52–08:30Z — batch 12: 25 dossiers; batch 12b: second dating pass (148 rows: 92 dated, 50 dropped).
* 10-11 08:50Z — final consolidation, `FINAL_SUMMARY.md`, README/HANDOFF refresh, final zip. **Done.**
