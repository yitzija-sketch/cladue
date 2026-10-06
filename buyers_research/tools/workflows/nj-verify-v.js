export const meta = {
  name: 'nj-verify-V',
  description: 'Verification: skeptic agents re-search sampled claims from the A/B/C part files against their source domains and record confirmed / refuted / unverifiable verdicts',
  phases: [{ title: 'Verify', detail: 'one skeptic agent per part file' }],
}

const RULES = `You are a verification subagent (a skeptic) for a New Jersey industrial real-estate research dataset. Other agents wrote data rows from web-search excerpts; your job is to re-check a sample of their claims and record a verdict per claim. You never add new research rows.

TOOLS / NETWORK: Use the Read tool to read the part file. Use the WebSearch tool to re-check claims (if it is not loaded, load it with ToolSearch "select:WebSearch"). WebFetch, curl and direct page fetches are BLOCKED by the network policy - do not use them. For each claim run at least two searches: one with allowed_domains set to the domain of the row's source URL (so the excerpt comes from the cited page) and one open search phrased differently (e.g. the address + town + "sold", or the firm + the quoted phrase in quotes, or the person's name + firm). Use mode "extended" when a standard search returns nothing relevant.

VERDICT RULES (be fair, not trigger-happy):
- "confirmed": a search excerpt from the cited domain or from an independent credible source states the same fact (same buyer, same price within rounding, same SF within 2%, same quote wording, person holds that title at that firm).
- "refuted": a credible source CONTRADICTS the claim (different buyer or seller for that address/date, different price by more than 10%, person is at a different firm or has a materially different title, the quote does not exist on that site, the entity belongs to a different sponsor). Give corrected_value when the source shows the correct value.
- "unverifiable": you could neither confirm nor contradict from search excerpts. This is NOT a refutation. Use it whenever the evidence is merely absent.
- Check the row's most consequential fields: for buyer rows: min_sf/max_sf/min_price/max_price, stated_criteria_quote (does that wording appear on that site?), acquisitions_head_name + title, nj_active; for deal rows: buyer, price, sf, date (year), seller, cap_rate when present; for entity rows: that the entity is actually tied to that buyer and the evidence_type/role are plausible.
- Do not spend more than ~5 searches on one row. Cover the sample size requested below.

OUTPUT: write ONE JSON object per line (JSONL) to the exact absolute path given below using the Write tool, one line per checked field. Fields in every row: workstream (A | B | C), part_file, row_key, field, verdict (confirmed | refuted | unverifiable), corrected_value, evidence_url, note. row_key MUST be copied EXACTLY from the part file so the consolidation step can match it: for A rows use the buyer_name string verbatim; for B rows use "<address>, <town>" copying address and town verbatim; for C rows use the entity_name string verbatim. field is the exact field name checked ("row" when the whole row is in question, e.g. the deal never happened). Write the file even if everything was unverifiable. Then return the structured summary. Your final answer is the structured output only.`

const SCHEMA = {
  type: 'object',
  properties: {
    part_file: { type: 'string' },
    rows_checked: { type: 'integer' },
    claims_checked: { type: 'integer' },
    confirmed: { type: 'integer' },
    refuted: { type: 'integer' },
    unverifiable: { type: 'integer' },
    worst_problems: { type: 'array', items: { type: 'string' }, description: 'refuted claims in one line each' },
    notes: { type: 'string' },
  },
  required: ['part_file', 'rows_checked', 'claims_checked', 'confirmed', 'refuted', 'unverifiable', 'worst_problems', 'notes'],
}

// args.targets = [{ key: 'V_A1', workstream: 'A', source: '/abs/path/part.jsonl', sample: 20, selection: 'text' }]
const TARGETS = (args && args.targets) || []
if (!TARGETS.length) throw new Error('args.targets required')

function promptFor(t) {
  const out = '/home/user/cladue/buyers_research/parts/V_verify/' + t.key + '.jsonl'
  return RULES + `\n\nTARGET: workstream ${t.workstream}. Read the part file ${t.source} (JSONL, one row per line). ${t.selection} Check up to ${t.sample} rows.` +
    `\n\nOUTPUT FILE (absolute path, JSONL): ${out}` +
    '\n\nWhen done, return the structured summary: part_file, rows_checked, claims_checked, confirmed, refuted, unverifiable, worst_problems, notes.'
}

phase('Verify')
log('Verification: ' + TARGETS.length + ' part files')
const results = await parallel(TARGETS.map(t => () => agent(promptFor(t), { label: 'V:' + t.key, phase: 'Verify', schema: SCHEMA })))
const out = results.filter(Boolean)
log('V done: ' + out.reduce((n, r) => n + (r.claims_checked || 0), 0) + ' claims checked; refuted ' + out.reduce((n, r) => n + (r.refuted || 0), 0))
return out
