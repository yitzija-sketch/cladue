# TURN_PLAN — remaining research, organised around the 200-searches-per-turn limit

**Constraint discovered 2026-10-06:** WebSearch allows **200 calls per turn, shared by every agent in
the turn** (the only web access in this environment; page fetches are blocked by network policy).
Round 1 launched 29 agents at once, so each got 5–16 searches and nine part files are empty.
Every batch below is sized to ≈185 searches (per-agent caps via `args.search_cap`) and each agent is
told to read its existing part file and append, and is handed the previous pass's leads
(`parts/_runs/LEADS.json`, built by `tools/leads_from_journals.py`).

A batch runs when a new turn starts (a message from the user, or a scheduled `send_later` message).
Launch command pattern (Workflow tool):
```
Workflow({ scriptPath: "<repo>/buyers_research/tools/workflows/<script>.js",
           args: { groups|slices|batches|targets: [...], search_cap: N, leads: <LEADS.json subset> } })
```
After each batch: `python3 -I buyers_research/tools/leads_from_journals.py && python3 -I buyers_research/tools/consolidate.py`, update RESEARCH_LOG §3/§4, commit.

| # | Status | Script | Slices (cap) | ≈searches |
|---|---|---|---|---|
| 1 | pending | nj-buyers-a | A3_national_pe_valueadd, A4_nynj_private_operators, A5_nj_developer_holders, A8_netlease_slb_foreign, A9_nontraded_reit_dst (30 each); A6_ios_truck, A7_cold_lastmile_smallbay (20 each) | 190 |
| 2 | pending | nj-deals-b | B_year_2021, B_year_2024 (35); B_year_2019, B_year_2020, B_year_2023 (30); B_year_2022 (25) | 185 |
| 3 | pending | nj-deals-b | B_geo_bergen, B_geo_hudson_essex, B_geo_union_passaic, B_geo_middlesex, B_geo_somerset_morris, B_geo_mercer_monmouth_burlington (30 each) | 180 |
| 4 | pending | nj-deals-b + nj-market-d | B_reit_industrial, B_reit_netlease_cold (30); D3_jll_kislak, D4_colliers_nai, D5_newmark_avison, D6_costar_rca_other (30) | 180 |
| 5 | pending | nj-buyers-a (custom groups) + nj-market-d | AX_1..AX_3 = buyers appearing in B deal rows but missing from A (from `consolidate_report.json: buyers_in_B_not_in_A`) (30 each); A1_public_reits, A2_institutional_core top-ups (25); D1, D2 top-ups (25) | 190 |
| 6–9 | pending | nj-entities-c | top-100 of `buyer_activity_rank.csv`, 5 buyers per agent, 5 agents per turn, cap 36 (≈7 searches/buyer) | 180 × 4 |
| 10 | pending | nj-verify-v | one skeptic per A part (9 × cap 12) + 4 B samplers (cap 20) | 188 |
| 11 | pending | nj-verify-v + nj-deals-b | 4 C samplers (cap 25) + B specialty sweeps: IOS/truck, cold storage, sale-leaseback, industrial land (3 × 30) | 190 |
| 12 | pending | dossiers (inline Agent calls or a small workflow) | 25 most active buyers, cap 7 each; built mostly from the CSVs | 175 |
| 13 | pending | — | final consolidation, README.md column dictionary, RESEARCH_LOG counts, summary; no searches | 0 |

Progress on this table is mirrored in RESEARCH_LOG.md §4 at each checkpoint.
