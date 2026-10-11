# HANDOFF — NJ Industrial Buyer Research (what this is, how to use it, how to continue)

Prepared 2026-10-11 for the broker (Eretz Realty) and anyone who picks this up later.
Status at hand-off: **batches 1–5 complete, entity discovery (batch 6–9) in progress** — see "What is still
running" below. Every number in this document is as of the snapshot date; the live files on the branch are
newer.

---

## 1. What this is, in one paragraph

A public-web research package that answers four questions for a New Jersey industrial broker:
**who is actively buying industrial property in North/Central NJ, what they say they want to buy, what they
actually bought in 2019–2024, and which legal entities (LLCs) they buy through.** It was built by ~70
parallel research agents searching the public web (trade press, brokerage press releases, SEC filings,
fund websites, brokerage market reports), each writing raw rows that a script then merged, normalised,
de-duplicated and validated into four CSV tables. It is designed to be **joined to your local tax-roll /
owner-graph database on the `name_key` columns** — it does not replace anything you already have, and it
never touched any other file in this repository (see `../NOTICE_buyers_research.md`).

This is lead and buy-box research for a broker. It is not investment advice.

## 2. The files you will actually use

| File | What is in it | Rows at snapshot |
|---|---|---|
| **`buyers_stated.csv`** | One row per buyer: who they are (HQ, website, type), their **stated** acquisition criteria (SF range, price range, product types, submarkets, hold strategy, deal structures, a verbatim quote and the URL it came from), the acquisitions head when publicly named, how active they are in NJ. | 377 buyers · 135 with sourced criteria · 262 confirmed NJ-active · 56 with a named acquisitions head |
| **`deals_public_2019_2024.csv`** | One row per NJ industrial property sold 2019–2024 as reported in the press / broker releases / REIT filings: date, address, town, county, buyer, seller, SF, price, $/SF, cap rate (rare), brokers, deal type, the buying LLC when the article named it. Portfolio deals have a `PORTFOLIO:` summary row plus per-building rows when addresses were listed. | 640 properties · 320 with price · 368 under 250,000 SF · 230 still undated (see §5) |
| **`buyer_entities.csv`** | One row per legal entity tied to a buyer: SPV LLCs, fund vehicles, GP/manager companies, former names, with the mailing/registered address and officer names when a public source shows them. This is the table that lets you recognise "XYZ Carlstadt LLC" on a tax bill as, say, Faropoint. | 133 entities for 25 buyers so far — 75 more buyers in progress |
| **`market_buyer_mix.csv`** | Market statistics pulled from free brokerage reports (C&W, CBRE, JLL, Colliers, NAI, Newmark, Avison Young, Lee, Savills, CoStar/CommercialEdge, Transwestern, IRR): vacancy, rents, absorption, sales volume, $/SF, cap-rate ranges, IOS land pricing, buyer-type commentary, by year/quarter/submarket. | 700 metric rows, 2019–2025 |
| `buyer_activity_rank.csv` | Helper: every buyer scored by how many 2019–24 press deals they appear in + NJ deals seen while researching + whether they have a buyer row. Used to pick the 100 buyers for entity research and the 25 for dossiers. | ~400 |
| `README.md` | Column-by-column dictionary for all four tables and the join-key rules. | — |
| `RESEARCH_LOG.md` | What was searched, what was blocked, what could not be found, counts per file, time-stamped checkpoints. | — |
| `dossier_*.md` | One-page briefs on the 25 most active buyers (**not yet written** — produced in the final batch). | — |

Supporting material (you can ignore unless you want to audit or re-run):
`parts/` = the raw rows every agent wrote (JSONL) plus each agent's own summary (`parts/_runs/*/journal.jsonl`);
`rejected_rows.csv` + `consolidate_report.json` = what the validator dropped and why, and all counts;
`tools/` = the merge/validate script and the agent orchestration scripts; `TASK_SPEC.md` = the original brief;
`RESUME.md` / `TURN_PLAN.md` / `KICKOFF_PROMPT.md` = how to restart the run in a new session.

## 3. How to read the tables (the five things that matter)

1. **`name_key` is the join key.** UPPERCASE, punctuation removed, the tokens LLC / INC / LP / CORP / THE
   removed, `&` → `AND`, single spaces. `buyer_name_key`, `seller_name_key`, `entity_name_key` follow the
   same rule. An alias table (`parts/_runs/ALIASES.json`) already folds JV labels and former names into one
   canonical buyer (Duke Realty → Prologis, EverWest → Sagard, "Longpoint Partners" → Longpoint Realty
   Partners, etc.), so one buyer = one key across all four files.
2. **Blank means "not found in a free public source" — never a guess.** No person, email or phone number
   was invented; emails appear only as `pattern: first.last@domain` and only when a real address at that
   domain was seen (2 rows). Phones are public office/branch numbers only (8 rows).
3. **`confidence`** — `high` = official filing / official press release / a named person quoted;
   `med` = the firm's own marketing page or a trade-press report; `low` = aggregator (traded.co etc.),
   secondhand or inferred. Anything inferred about a buy box lives in `notes` prefixed `INFERRED:`, never
   in the criteria columns.
4. **Every row has a `source_url`** (or `criteria_source_url` / `evidence_url`) that appeared in the
   researcher's search results. Rows without one were dropped into `rejected_rows.csv`.
5. **Numbers are plain**: `price` 18500000 not "$18.5M"; `cap_rate` 5.75 for 5.75%; `sf` in square feet;
   dates `YYYY-MM-DD`, or `YYYY-MM` / `YYYY` when the source was less precise.

## 4. What the data says so far (headline findings)

**Most active press-visible buyers of NJ industrial, 2019–2024** (by deal rows + NJ activity seen):
Devli Real Estate (Weehawken/Wallington; Meadowlands small-mid buildings, 12 deals), Seagis Property Group
(Conshohocken PA; 13 deals; value-add infill, 21'+ clear, trailer parking), Prologis (14 deals incl. legacy
Duke), Sitex Group (14 — already on your port call list), Faropoint (10; stated 20K–100K SF small-bay buy
box; Hoboken c/o address), Longpoint Realty Partners (10; Boston; value-add infill), CenterPoint (9 — call
list), Terreno (8 — call list), Sagard Real Estate ex-EverWest (8), The STRO Companies (Fairfield/Florham
Park/Clifton; small-to-medium value-add and stabilised), Commerce Park Investors / Legacy RE Developers
(Morris County small-bay), Dalfen Industrial (last-mile + IOS, Centerbridge equity), Morgan Stanley REI with
Saxum (East Hanover $217.5M 7-building), Realterm (IOS / final-mile; Annapolis fund address), Thor Equities
(Newark/Passaic/Bogota), Venture One (VK Industrial VI LP with Kovitz), Ambient Capital Partners (IOS;
Harrison/Kearny $156M), Ares Industrial REIT (Wayne $138.5M; SPV convention `BCI IV <property> DC LLC` →
`AIREIT <property> DC LLC`), Brookfield, Marcus Partners, Velocity Venture Partners, Bridge Logistics
Properties, Invesco, Link Logistics, Ridgecut Road.

**Buy boxes with hard numbers** (all sourced; see `stated_criteria_quote` + `criteria_source_url`):
Penwood $10–100M+ value-add NY/NJ incl. IOS/cold/last-mile · High Street Logistics $3–250M, 24' clear, ≤10%
office, built after 1980 · Faropoint 20K–100K SF small-bay · Jadian IOS $2–50M+, 2+ usable acres, all-cash
· Timber Hill $5–75M, 3–100 acres, 10K–250K SF · Industrial Outdoor Ventures $2–50M+, top-20 MSA infill ·
Calare $10–50M Northeast middle-market industrial/flex · Zurich AAM $15–100M fully leased · Four Springs /
Pilothouse $5–25M single-tenant net lease (Belmar NJ HQ) · STAG, Gladstone ($5–50M), W. P. Carey
($5–500M), Broadstone ($5–300M), LCN ($20–400M), ElmTree ($20–150M+) · Lovett 100K SF–5M SF portfolios ·
Cohen Asset Management (Meadowlands shallow-bay specialist, ASB JV) · Bain/Oliver Street (Class B infill,
~23K SF suites).

**Buyer types with little public information** (expect to rely on your local tax-roll graph instead):
family offices and 1031 private buyers (only 5 rows typed "family office"; most small-LLC buyers have a
deal row and nothing else), owner-users (70 rows but no criteria by nature), and foreign capital in
sub-250K SF product (Korean/German/Japanese funds appear only in big-box BTS deals).

**Market colour** (from `market_buyer_mix.csv`): NJ led the nation in industrial sales volume in Q1 2025
(~$256/SF statewide average per CommercialEdge); NAI reports $239/SF (H2 2023) → $180–190/SF (2024–25) vs
a $200+ peak in 2022, mid-5% cap rates in Q1 2024; CBRE cap-rate survey NJ rows 2023–24; IOS land in
Central NJ quoted at $8–10K/acre/month rent and up to $7M/acre (Moonachie) in sales; vacancy climbed from
~2% (2021–22) to 7–9% (2025) as 2023–24 deliveries landed.

## 5. Limits you should know before relying on a row

* **Search-excerpt based.** This cloud environment blocked direct page fetches, so every fact came from
  search-result excerpts (which do include sec.gov filings, PDF reports and article text) rather than full
  page reads. Consequence: some cells are blank that a full read would fill (HQ street addresses,
  acquisitions-head names, deal dates in re-nj.com articles whose URLs carry no date).
* **230 deal rows are undated** (`date` blank, notes say `DATE UNVERIFIED`). They are real transactions
  from the 2019–2024 window as far as the article shows, but the exact year was not in the excerpt; a
  dating pass is scheduled in the verification batch, and your tax-roll last-sale date will resolve the
  rest on join.
* **Verification pass not yet run.** The `verification` column is empty until batch 10–11 runs; after it,
  rows carry `confirmed:<field>` / `refuted-blanked:<field>` / `unverifiable:<field>` tags.
* **A few mis-dated deals from earlier passes were caught and removed** (e.g. Kurv's Carlstadt portfolio
  is a 2026 deal). Their keys are in `parts/_runs/EXCLUDE_B.jsonl`; if you spot another, add a line there
  and re-run the consolidator.
* **Entity table is partial** (25 of 100 buyers at snapshot). SEC 10-K Exhibit 21 and Form D subsidiaries
  were deliberately *not* re-collected because your local EDGAR sweep already has them; the agents focused
  on Schedule III property names, "affiliate of" press, loan/financing releases, Form ADV fund names,
  municipal records and naming patterns.
* The repo's `cloud_context/` folder (your list of already-known buyers and press deals) was **not present
  on any branch**, so the "skip what is already local" rule was applied from the brief's own text (no
  2025–26 press deals; minimal effort on CenterPoint, Terreno, Cabot, Sitex, Elberon, Kurv). Some overlap
  with your local data is therefore likely — the join will show it.

## 6. How it was built (so you can trust or audit it)

* **Workstream A (buy boxes)** — 12 agents, one per buyer type (public REITs; institutional core funds;
  national PE/value-add; NY/NJ private operators; NJ developer-holders; IOS/truck; cold storage/last-mile/
  small-bay; net-lease/sale-leaseback/foreign; non-traded REIT/DST; plus three "expansion" groups built
  from buyers that appeared in deal rows but had no buyer row: institutional, owner-users, private/small
  LLCs). Each agent verified seeds, searched firm criteria pages, investor decks, SEC business sections,
  press quotes and team pages.
* **Workstream B (deals)** — 14 agents: one per year 2019–2024 sweeping ~25 publications/newsrooms, six
  county-cluster sweeps (town by town, trade-press-constrained, also date-verifying the year agents'
  undated rows), two REIT-disclosure sweeps (acquisition press releases, 10-K Schedule III).
* **Workstream C (entities)** — 20 batches of 5 buyers (top-100 by activity, call-list buyers excluded);
  each agent hunts SPV/fund/manager names, addresses and officers across sec.gov, press, financing
  releases, municipal planning records and registries, and reports the naming pattern it finds.
* **Workstream D (market stats)** — 6 agents, one per brokerage group, plus capital-markets top-ups.
* **Merge/validate** — `tools/consolidate.py`: normalises numbers and dates, fills county from town,
  rejects out-of-scope counties/years and rows without a source URL, merges duplicates (same address+town+
  year; same buyer name_key) keeping the most complete row and the highest confidence, applies the alias
  table and the exclusion list, computes $/SF when price and SF are both stated, and writes the ranking.
* **Budget mechanics** — the environment allows 200 web searches per turn shared by all agents, so the
  work ran as ~13 batches of ~7 agents (each with a hard per-agent cap), with every batch committed and
  pushed before the next started. A credit lapse on 2026-10-06 paused the run mid-batch 6; nothing was
  lost and it resumed 2026-10-11.

## 7. What is still running / what comes next

| Step | Status |
|---|---|
| Entity discovery, buyers 26–100 (batches 7–9) | running / queued |
| Verification: skeptic agents re-check ~10 rows per buyer file and ~8 per deal file; dating pass on undated deals; specialty deal sweeps (IOS, cold storage, sale-leaseback, land) | queued |
| 25 one-page buyer dossiers (`dossier_<buyer>.md`) | queued (final batch) |
| Final `RESEARCH_LOG.md` counts + summary (top-20 buyers, thin buyer types, top-10 open questions) | last step |

Each step is pushed to the branch as it completes; the final zip will be sent when the last step lands.

## 8. If you need to restart it yourself

Open a new Claude Code session on branch `claude/nj-industrial-buyer-research-v4j2sy` and paste the
message in `KICKOFF_PROMPT.md`. It reads `TASK_SPEC.md` (the brief), `RESUME.md` (state and mechanics) and
`TURN_PLAN.md` (which batch is next) and continues. To rebuild the CSVs from the raw parts at any time:
`python3 -I buyers_research/tools/consolidate.py`.

## 9. Where everything is

GitHub: https://github.com/yitzija-sketch/cladue/tree/claude/nj-industrial-buyer-research-v4j2sy/buyers_research
Session that built it: https://claude.ai/code/session_0126gXTSDEH4CeHTDhskFo5J
