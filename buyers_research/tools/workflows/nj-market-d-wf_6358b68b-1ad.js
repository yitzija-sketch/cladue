export const meta = {
  name: 'nj-market-D',
  description: 'Workstream D: market-level NJ industrial buyer statistics from free brokerage and data-provider reports, one agent per brokerage group',
  phases: [{ title: 'Market stats', detail: 'one agent per brokerage group; each writes a JSONL part file' }],
}

const RULES = `You are a research subagent for a New Jersey industrial real-estate broker. Your output is DATA that will be machine-joined to a local property graph; structure matters more than prose.

TOOLS / NETWORK: Use the WebSearch tool (if it is not loaded, load it with ToolSearch query "select:WebSearch"). WebFetch, curl and every direct page fetch are BLOCKED by this environment's network egress policy - do not use them (if you try once and see EGRESS_BLOCKED, do not retry). WebSearch returns result URLs plus excerpts/summaries of page content (including PDF reports); extract numbers ONLY from what those results actually state, and attribute each number to the result URL that carries it. Use mode "extended" for report-specific queries and "standard" for simple lookups. Use allowed_domains to sweep one firm's site at a time. Run MANY searches (aim for 50-90): one per firm x report type x year x quarter where reports exist, plus press coverage of those reports (ROI-NJ, NJBIZ, re-nj.com, GlobeSt, Commercial Observer, Bisnow, The Real Deal often summarize the numbers). You have a large budget; be exhaustive. Write a first version of your output file halfway through and overwrite it at the end.

HARD RULES:
1. Public free web only. No logins, accounts, forms, CAPTCHAs, paywalls (if a report requires a form to download, use only what the search excerpt or a press article shows). Never contact anyone.
2. Every row needs a source_url that appeared in your search results and supports the number. If you cannot source a number, do not write it. Never guess.
3. Geography: Northern NJ, Central NJ, "New Jersey" statewide industrial, and submarkets: Meadowlands, Port / Newark-Elizabeth / Ports, I-95 / NJ Turnpike corridor, I-78 corridor, I-287 corridor, Route 1 / Exit 8A / Exit 7A, Bergen County, Hudson/Essex (Newark), Middlesex, Morris, Somerset, Union, Mercer, Monmouth, Burlington / Southern NJ when part of a "Central/South" report. Years 2019 through 2025 (2025 is fine here because these are market statistics, not deal records).
4. Numbers: value is a plain number (no $, commas, %, "SF"); put the unit in unit (USD | USD_millions | USD/SF | USD/acre | percent | SF | SF_millions | count | years | rank | bps). If a report gives a range (e.g. cap rates 5.0%-5.5%), write two rows with metric suffixes "_low" and "_high". Dates YYYY-MM-DD or YYYY-MM or YYYY.
5. One row per metric value. size_band: "<50K", "50-100K", "100-250K", "250-500K", "500K+", or "all" when not broken out (use the report's own bands if different, written the same way). metric vocabulary (use these when they fit): sales_volume, sales_volume_industrial, sale_count, avg_price_psf, median_price_psf, cap_rate, cap_rate_low, cap_rate_high, cap_rate_class_a, cap_rate_class_b, buyer_share_institutional, buyer_share_private, buyer_share_user, buyer_share_foreign, buyer_share_reit, buyer_share_other, top_buyer_mention (value = rank or 1; notes = buyer name and what was said), top_seller_mention, land_value_per_acre, ios_rent_per_acre_month, ios_price_per_acre, vacancy_rate, availability_rate, asking_rent_psf, net_absorption_sf, under_construction_sf, deliveries_sf, leasing_volume_sf, avg_deal_size_sf, price_psf_small_bay, price_psf_last_mile, cold_storage_price_psf, cold_storage_cap_rate, trend_statement (value = 1; notes = the quantified trend sentence, max 30 words). Keep context (class, tenancy, whether it is a trailing-12-month figure) in notes.
6. source_name = the report/article title (e.g. "Cushman & Wakefield Northern New Jersey Industrial MarketBeat Q4 2022"); source_url = the URL from the results; source_date = publication date.
7. OUTPUT: write ONE JSON object per line (JSONL) to the exact absolute path given below using the Write tool. Fields in every row: year, quarter (Q1 | Q2 | Q3 | Q4 | H1 | H2 | FY | ""), submarket, size_band, metric, value, unit, source_name, source_url, source_date, notes. Write the file even if you found little. Then return the structured summary requested. Your final answer is the structured output only - no prose report.`

const ALL_GROUPS = [
  { key: 'D1_cushman_savills', task: 'FIRMS: Cushman & Wakefield (Northern New Jersey Industrial MarketBeat, Central New Jersey Industrial MarketBeat, New Jersey industrial capital markets / investment sales reports, U.S. industrial MarketBeat NJ pages, C&W NJ "year in review" press, Cushman NJ cap-rate commentary) and Savills (New Jersey industrial market reports, Savills Northern NJ industrial, Savills industrial investment outlook). Also capture press articles quoting C&W / Savills NJ numbers (sales volume, $/SF, cap rates, buyer types, IOS and cold-storage trends).' },
  { key: 'D2_cbre_lee', task: 'FIRMS: CBRE (New Jersey Industrial Figures / MarketView quarterly, CBRE Northern & Central NJ industrial, CBRE U.S. Cap Rate Survey industrial New York/New Jersey rows, CBRE NJ investment sales press) and Lee & Associates New Jersey (industrial market reports, Lee & Associates NJ quarterly, national industrial report NJ rows). Also capture press articles quoting CBRE / Lee NJ numbers (sales volume, $/SF, cap rates, buyer types, IOS and cold-storage trends).' },
  { key: 'D3_jll_kislak', task: 'FIRMS: JLL (New Jersey Industrial Insight / Market Dynamics quarterly, JLL NJ industrial capital markets, JLL "New Jersey industrial sales volume", JLL Industrial Outdoor Storage reports with NJ data, JLL cold storage reports with NJ data) and The Kislak Company (NJ industrial sales statistics, Kislak market updates). Also capture press articles quoting JLL / Kislak NJ numbers (sales volume, $/SF, cap rates, buyer types, IOS and cold-storage trends).' },
  { key: 'D4_colliers_nai', task: 'FIRMS: Colliers (New Jersey Industrial Market Report quarterly, Colliers Northern/Central NJ, Colliers NJ capital markets snapshot, Colliers national industrial report NJ rows) and NAI James E. Hanson / NAI DiLeo-Bram / NAI Mertz / NAI Fennelly (Northern NJ industrial market reports, NAI Hanson quarterly, NAI Mertz Southern/Central NJ). Also capture press articles quoting Colliers / NAI NJ numbers (sales volume, $/SF, cap rates, buyer types, IOS and cold-storage trends).' },
  { key: 'D5_newmark_avison', task: 'FIRMS: Newmark (New Jersey Industrial Market Report quarterly, Newmark NJ capital markets, Newmark industrial investment sales NJ, Newmark IOS research) and Avison Young (New Jersey industrial market report, AY NJ quarterly, AY industrial investment NJ, AY Northeast IOS reports). Also capture press articles quoting Newmark / Avison Young NJ numbers (sales volume, $/SF, cap rates, buyer types, IOS and cold-storage trends).' },
  { key: 'D6_costar_rca_other', task: 'SOURCES: CoStar News free articles on New Jersey industrial sales volume / pricing / cap rates; MSCI Real Capital Analytics commentary on Northern New Jersey industrial (volume, cap rates, buyer composition, cross-border share); GlobeSt, Commercial Observer, Bisnow, The Real Deal, ROI-NJ, NJBIZ, re-nj.com, NJ Business Magazine, Real Estate NJ annual "year in review" and "most active buyers" pieces; Transwestern NJ industrial reports; Marcus & Millichap New Jersey industrial investment forecast; Trepp / Moody\'s / Green Street notes on NJ industrial; Integra Realty Resources Viewpoint Northern NJ industrial; Cushman/JLL/CBRE "Industrial Outdoor Storage" national reports for Northern NJ rows; Lineage / Americold or cold-storage reports with NJ rows; NAIOP NJ or Rutgers reports on NJ warehouse market. Capture buyer-type shares, cross-border share, top-buyer lists, $/SF by size band, cap rates, volume by year, IOS land $/acre, cold storage pricing.' },
]

const wanted = (args && args.groups) || ALL_GROUPS.map(g => g.key)
const GROUPS = ALL_GROUPS.filter(g => wanted.includes(g.key))

const D_SCHEMA = {
  type: 'object',
  properties: {
    part_file: { type: 'string' },
    rows_written: { type: 'integer' },
    reports_used: { type: 'array', items: { type: 'string' } },
    searches_run: { type: 'integer' },
    blocked: { type: 'array', items: { type: 'string' } },
    not_found: { type: 'array', items: { type: 'string' } },
    notes: { type: 'string' },
  },
  required: ['part_file', 'rows_written', 'reports_used', 'searches_run', 'blocked', 'not_found', 'notes'],
}

function promptFor(g) {
  const path = '/home/user/cladue/buyers_research/parts/D_market/' + g.key + '.jsonl'
  return RULES + '\n\nTASK (Workstream D - market-level buyer statistics 2019-2025 for Northern/Central NJ industrial). ' + g.task +
    '\nSearch shapes: "<firm> New Jersey industrial market report Q3 2022", "<firm> Northern New Jersey industrial MarketBeat 2021", "<firm> New Jersey industrial sales volume 2023 cap rate", "<firm> New Jersey industrial investment sales buyers institutional private", "New Jersey industrial cap rates 2024 <firm>", "New Jersey industrial price per square foot record <firm>", "industrial outdoor storage New Jersey <firm> report", "cold storage New Jersey <firm> report", and press coverage: "<firm> report New Jersey industrial" with allowed_domains for roi-nj.com, njbiz.com, re-nj.com, globest.com, commercialobserver.com, bisnow.com.' +
    '\n\nOUTPUT FILE (absolute path, JSONL): ' + path +
    '\n\nWhen done, return the structured summary: part_file, rows_written, reports_used (titles), searches_run, blocked, not_found (report series you could not locate), notes.'
}

phase('Market stats')
log('Workstream D: ' + GROUPS.length + ' brokerage groups')
const results = await parallel(GROUPS.map(g => () => agent(promptFor(g), { label: 'D:' + g.key, phase: 'Market stats', schema: D_SCHEMA })))
const out = results.filter(Boolean)
log('D done: ' + out.reduce((n, r) => n + (r.rows_written || 0), 0) + ' rows across ' + out.length + ' parts')
return out