# RESUME.md — how to pick this research up if the session stops

Everything the run has produced is in this folder and is committed/pushed every ~10 minutes by
`tools/checkpoint.sh` (branch `claude/nj-industrial-buyer-research-v4j2sy`).

## What is where

| Path | Meaning |
|---|---|
| `parts/A_buyers/*.jsonl` | Workstream A raw rows (one JSON object per line, one buyer per row) written by each subagent |
| `parts/B_deals/*.jsonl` | Workstream B raw deal rows 2019–2024 |
| `parts/C_entities/*.jsonl` | Workstream C raw entity rows |
| `parts/D_market/*.jsonl` | Workstream D raw market-metric rows |
| `parts/V_verify/*.jsonl` | Verification verdicts (`workstream,row_key,field,verdict,corrected_value,evidence_url,note`) |
| `parts/_runs/<run_id>/journal.jsonl` | Each workflow's agent-by-agent return values (counts, buyers seen, blocked, not found) |
| `parts/_runs/STATUS.txt` | Row count per part file at the last checkpoint |
| `tools/workflows/*.js` | The exact Workflow scripts that were run (self-contained; `args` selects slices) |
| `tools/consolidate.py` | Rebuilds all deliverable CSVs from `parts/` — safe to run at any time |
| `tools/checkpoint.sh` | The auto-commit loop |
| `RESEARCH_LOG.md` | Running log: setup findings, method, blocked items, counts |

## KEY CONSTRAINT (read before launching anything)

WebSearch is capped at **200 calls per turn, shared by all agents in the turn**; page fetches are
blocked by network policy, so WebSearch is the only web access. Run at most ~7 agents per turn with
`args.search_cap` set so the total stays ≈185, and follow `TURN_PLAN.md` batch by batch. Each new
message from the user (or a scheduled `send_later` message) starts a new turn and resets the budget.
Raising `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` in the environment's variables (new session) lifts it.

## Pipeline and status checklist

Mark-up is updated at each checkpoint (see `RESEARCH_LOG.md` §4 for timestamps).

1. [launched] **A** buy boxes — 9 groups. Scripts: `tools/workflows/nj-buyers-a-*.js`.
   Launched as two runs: `args={"groups":["A1_public_reits","A2_institutional_core","A3_national_pe_valueadd","A4_nynj_private_operators","A5_nj_developer_holders"]}` (run `wf_2a123455-be7`)
   and `args={"groups":["A6_ios_truck","A7_cold_lastmile_smallbay","A8_netlease_slb_foreign","A9_nontraded_reit_dst"]}` (run `wf_d5bb347b-261`).
   A group is complete when `parts/A_buyers/<group>.jsonl` exists and its summary is in the run journal.
2. [launched] **B** deals — 14 slices. Scripts: `tools/workflows/nj-deals-b-*.js`.
   Runs: `wf_44d93a53-519` (`B_year_2019, B_year_2020, B_year_2021, B_geo_bergen, B_geo_hudson_essex, B_geo_union_passaic, B_reit_industrial`)
   and `wf_b9057fc4-86b` (`B_year_2022, B_year_2023, B_year_2024, B_geo_middlesex, B_geo_somerset_morris, B_geo_mercer_monmouth_burlington, B_reit_netlease_cold`).
3. [launched] **D** market stats — 6 groups, run `wf_6358b68b-1ad`, script `tools/workflows/nj-market-d-*.js`.
   **Round-1 result (budget-starved):** A1 (28 rows), A2 (39), A6 (14), A7 (19) written; A3, A4, A5, A8, A9
   empty → TURN_PLAN batch 1. B: 2019 (22), 2020 (12), 2022 (51), 2023 (14) written; 2021, 2024, all six
   geo slices and both REIT slices empty → batches 2–4. D: D1 (45), D2 (96) written; D3–D6 empty → batch 4.
4. [pending] **A-expansion** — `buyers_in_B_not_in_A` in `consolidate_report.json` (26 names after round 1,
   e.g. Seagis, Thor Equities, Turnbridge, Penwood, Taconic, Woodmont, Velocity, Marcus Partners, Bridge
   Logistics Properties) → A-style agents writing `parts/A_buyers/AX_<n>.jsonl` (TURN_PLAN batch 5).
   To pass custom groups to `nj-buyers-a.js`, add them to `ALL_GROUPS` in the script (key `AX_<n>`).
5. [pending] **C** entities — top ~100 of `buyer_activity_rank.csv`, 5 buyers per agent, script
   `tools/workflows/nj-entities-c.js` with `args.batches=[{key:'C_01',buyers:[{name,type,context}]}]` (batches 6–9).
6. [pending] **V** verification — `tools/workflows/nj-verify-v.js` with `args.targets` (batches 10–11).
7. [pending] **Consolidate** — `python3 -I tools/consolidate.py` → `buyers_stated.csv`,
   `deals_public_2019_2024.csv`, `buyer_entities.csv`, `market_buyer_mix.csv`, `buyer_activity_rank.csv`,
   `rejected_rows.csv`, `consolidate_report.json`.
8. [pending] **E** dossiers — 25 most active buyers → `dossier_<slug>.md`.
9. [pending] `README.md` (column dictionary) and final `RESEARCH_LOG.md` counts + summary.

## How to re-run or resume a workflow in a new Claude Code session

* To finish missing slices only: invoke the Workflow tool with the script from `tools/workflows/` and
  `args` listing just the slice/group keys whose part file is missing (each script filters on `args`).
* The environment blocks WebFetch/curl (network policy); agents must use WebSearch only. If Network
  access is broadened, the prompts still work and verification gets stronger.
* `tools/consolidate.py` is idempotent — run it whenever new part files land.
