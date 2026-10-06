# NOTICE — what the buyer-research session added (and did not touch)

Session: https://claude.ai/code/session_0126gXTSDEH4CeHTDhskFo5J · Branch: `claude/nj-industrial-buyer-research-v4j2sy`

**Nothing pre-existing in this repository was modified, moved, deleted or reformatted.**
`CostarExport_TrueOwners.xlsx`, `drafts.json`, `outreach/` (Code.gs, README.md, recipients.csv) and
`.gitignore` are byte-for-byte as they were at commit `0d9c48c`.

Everything the research produced lives in **one new folder**, `buyers_research/`, plus this notice:

| Added | Purpose |
|---|---|
| `buyers_research/buyers_stated.csv` | Workstream A — stated buy boxes of NJ industrial buyers |
| `buyers_research/deals_public_2019_2024.csv` | Workstream B — press-sourced NJ industrial sales 2019–2024 |
| `buyers_research/buyer_entities.csv` | Workstream C — SPV / GP / manager entities per buyer |
| `buyers_research/market_buyer_mix.csv` | Workstream D — market-level buyer statistics |
| `buyers_research/buyer_activity_rank.csv` | helper — activity ranking used to pick C/E targets |
| `buyers_research/rejected_rows.csv`, `consolidate_report.json` | validation output (rows dropped and why; counts) |
| `buyers_research/dossier_*.md` | Workstream E — one-page buyer dossiers |
| `buyers_research/README.md`, `RESEARCH_LOG.md`, `RESUME.md` | column dictionary, research log, pick-up instructions |
| `buyers_research/parts/` | raw JSONL part files written by each research agent + workflow journals |
| `buyers_research/tools/` | `consolidate.py` (rebuilds CSVs from parts), `checkpoint.sh` (auto-commit), `workflows/*.js` (agent orchestration scripts) |

If any of this conflicts with your local database, the local data wins: these files are *inputs to join*,
never replacements. Join on the `name_key` helper columns (UPPERCASE, punctuation and LLC/INC/LP/CORP/THE removed).
