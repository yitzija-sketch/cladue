# RESEARCH_LOG — NJ industrial buyer research (public-web arm)

Status: **IN PROGRESS** (this file is updated at each checkpoint; if the session lapsed, the
`parts/` folder holds everything agents had written and `tools/consolidate.py` rebuilds the CSVs
from it — run `python3 -I buyers_research/tools/consolidate.py`).

Session: https://claude.ai/code/session_0126gXTSDEH4CeHTDhskFo5J  · Started 2026-10-06 (UTC)

## 0. Setup findings

* `cloud_context/` **was not present in the repository** (checked every branch:
  `claude/gallant-cori-3RKMI`, `claude/nj-buckingham-avenue-records-b9wgyd`, this branch).
  `known_buyers_already_in_local_graph.csv` therefore could not be used. Fallback: the exclusions in
  the task text were applied (no 2025–2026 press deals; minimal effort on the Elizabeth-port call
  list — CenterPoint, Terreno, Cabot, Sitex, Elberon, Kurv/Bridge). Deal history for *all* buyers was
  collected from press (not tax records), so nothing here duplicates the local tax-roll work.
* **Network policy**: this cloud environment blocks every direct page fetch (WebFetch / curl) —
  tested `re-nj.com`, `www.sec.gov`, `efts.sec.gov`, `data.sec.gov`, `rebusinessonline.com`,
  `www.prologis.com` → `EGRESS_BLOCKED`. **WebSearch works** and returns page excerpts (including
  sec.gov Schedule III content and trade-press deal details), so all research is search-derived.
  Consequence: quotes and numbers come from search excerpts, not full page reads; a separate
  verification pass re-searches each important claim against its source domain. Broadening the
  environment's Network access would allow full 10-K Schedule III / criteria-page reads.
* No logins, forms, CAPTCHAs or paywalls were used. Nobody was contacted.

## 1. Method

Parallel research subagents (Workflow tool), each writing one JSONL part file under
`buyers_research/parts/`, then a deterministic consolidation step (`tools/consolidate.py`) that
concatenates, normalises `name_key`, dedupes, validates (non-empty `source_url`, parseable dates,
numeric SF/price/cap-rate, in-scope county/years) and writes the deliverable CSVs plus
`rejected_rows.csv` and `consolidate_report.json`.

| Workstream | Split | Part files | Run IDs |
|---|---|---|---|
| A – stated buy boxes | 9 buyer-type groups (public REITs; institutional core; national PE/value-add; NY/NJ private operators; NJ developer-holders; IOS/truck; cold/last-mile/small-bay; net-lease/SLB/foreign; non-traded REIT/DST) | `parts/A_buyers/A1..A9*.jsonl` | wf_2a123455-be7 (A1–A5), wf_d5bb347b-261 (A6–A9) |
| B – deals 2019–2024 | 6 year slices (all publications) + 6 geographic slices (county clusters × all years) + 2 REIT-disclosure slices | `parts/B_deals/B_*.jsonl` | wf_44d93a53-519, wf_b9057fc4-86b |
| D – market stats | 6 brokerage groups (C&W+Savills; CBRE+Lee; JLL+Kislak; Colliers+NAI; Newmark+AY; CoStar/RCA/other) | `parts/D_market/D*.jsonl` | wf_6358b68b-1ad |
| A-expansion | buyers that appear in B deal rows but not in A | `parts/A_buyers/AX_*.jsonl` | (after A+B) |
| C – entities | batches of the ~100 most active buyers (ranked by B deal rows + A activity) | `parts/C_entities/C_*.jsonl` | (after A+B) |
| V – verification | skeptic agents re-search a sample of A/B/C claims against the source domain | `parts/V_verify/V_*.jsonl` | (after A/B/C) |
| E – dossiers | 25 most active buyers | `dossier_<slug>.md` | (after consolidation) |

## 2. Searches run / blocked / not found

(filled in from agent summaries at each checkpoint — see section 4 for the latest)

## 3. Counts per file

(filled in by the consolidation step)

## 4. Checkpoint notes

* 2026-10-06 ~18:30Z — Workflows A (2), B (2), D (1) launched; consolidation tool written; auto-checkpoint
  loop started (commits + pushes `buyers_research/` every ~10 minutes).
