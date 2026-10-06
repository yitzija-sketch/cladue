export const meta = {
  name: 'nj-entities-C',
  description: 'Workstream C: shell entities, GP/manager entities, addresses and signatories for the most active NJ industrial buyers, batched 4-5 buyers per agent',
  phases: [{ title: 'Entities', detail: 'one agent per buyer batch; each writes a JSONL part file' }],
}

const RULES = `You are a research subagent for a New Jersey industrial real-estate broker. Your output is DATA that will be machine-joined to a local property graph in which owners appear as SPV LLC names and mailing addresses; structure matters more than prose.

TOOLS / NETWORK: Use the WebSearch tool (if it is not loaded, load it with ToolSearch query "select:WebSearch"). WebFetch, curl and every direct page fetch are BLOCKED by this environment's network egress policy - do not use them (if you try once and see EGRESS_BLOCKED, do not retry). WebSearch returns result URLs plus excerpts/summaries of page content (including sec.gov filings, PDF press releases, municipal PDFs); extract facts ONLY from what those results actually state, and attribute each fact to the result URL whose title/content carries it. Use mode "extended" for filing- and entity-specific queries. Use allowed_domains to target one site at a time (["sec.gov"], ["opencorporates.com"], a town's .gov/.org site, ["commercialobserver.com"], ["traded.co"], the buyer's own domain). Vary wording across queries. Your WebSearch call cap is stated at the end of this prompt and is a hard limit. Write a first version of your output file halfway through and overwrite it with the complete version at the end.

HARD RULES:
1. Public free web only. No logins, accounts, forms, CAPTCHAs, paywalls. Official registries only when the result page is freely viewable in the search excerpt. Never contact anyone.
2. Every row needs an evidence_url that appeared in your search results and supports the row. If you cannot source a fact, leave the cell empty (""). Never guess an LLC name - record only names that actually appear in a source. Never invent people.
3. confidence: "high" = SEC filing, official registry page, official press release, municipal resolution/ordinance; "med" = trade press ("an affiliate of X", "XYZ Carlstadt LLC, an entity controlled by X"), lender/broker financing release; "low" = aggregator (Bizapedia, OpenCorporates mirror, LoopNet-type) or inference from a naming pattern. A naming-pattern inference must say "INFERRED:" in notes.
4. Already done locally (lower priority, do not spend effort on): 10-K Exhibit 21 subsidiary lists and Form D filings already matched to NJ owners; tax-roll and deed data. PRIORITISE instead: Schedule III property-level names and the SPV names in loan documents / 8-Ks; Form ADV Schedule D private-fund names and the adviser's registered address; "affiliate of" press mentions; lender/CMBS/financing press naming the borrower LLC; municipal planning-board / PILOT / redevelopment documents naming the applicant LLC; UCC or permit excerpts; the manager/GP entity and the mailing address the fund uses (its HQ, or "c/o" address) so the broker can match tax-bill mailing addresses.
5. For each buyer also record: the top-level operating entity (entity_role "manager" or "GP") with its registered/HQ address; fund vehicles (entity_role "fund", e.g. "XYZ Industrial Fund IV LP"); former names and merged predecessors (entity_role "former name", e.g. Duke Realty Limited Partnership -> Prologis; Monmouth Real Estate -> ILPT; Gramercy -> GLP); JV partner entities (entity_role "affiliate"); and every property-level SPV you can source (entity_role "SPV") - in notes give the NJ property address/town the SPV holds when known.
6. name keys: name_key (of the buyer) and entity_name_key = the name in UPPERCASE with punctuation removed and the tokens LLC, INC, LP, CORP, THE removed, single-spaced. Keep entity_name itself verbatim as it appears in the source (with LLC / L.P. etc.).
7. OUTPUT: write ONE JSON object per line (JSONL) to the exact absolute path given below using the Write tool. Fields in every row, in this order: buyer_name, name_key, entity_name, entity_name_key, entity_role (SPV | GP | manager | fund | affiliate | former name), state_of_formation, mailing_or_registered_address, signatory_or_officer_names, evidence_type (10-K Schedule III | 10-K Ex.21 | Form D | Form ADV | 8-K/loan doc | UCC | deed recital | press | loan press | NJ/DE filing | municipal record | permit | ownership note), evidence_url, confidence (high | med | low), notes. One row per entity (dedupe within your file). Write the file even if you found little. Then return the structured summary requested. Your final answer is the structured output only - no prose report.`

const TASK = `TASK (Workstream C - shell-entity and address discovery). For EACH buyer below find the legal entities it buys and holds NJ industrial property through. Query shapes per buyer:
- SEC (allowed_domains ["sec.gov"]): "<buyer> Schedule III <NJ town>", "<buyer> 10-K properties New Jersey Carlstadt Elizabeth Kearny Edison Secaucus", "<buyer> Form ADV private fund", "<buyer> 8-K loan agreement borrower LLC New Jersey", "<buyer> Industrial Fund LP".
- Press: "affiliate of <buyer>" New Jersey; "<buyer>" "LLC" acquires New Jersey warehouse; "entity controlled by <buyer>"; "<buyer>" "c/o"; "<buyer> loan" New Jersey warehouse (financing releases by Meridian, JLL, Walker & Dunlop, CBRE, Berkadia, Greystone, lender press: "provided a $XX million loan to an affiliate of <buyer> secured by ... New Jersey").
- Naming patterns: "<buyer short name> <town> LLC" for the towns in the buyer's known deals, "<buyer short name> NJ LLC", "<buyer short name> Logistics LLC", "<buyer short name> Property Owner LLC", "<buyer short name> Industrial" "LLC" New Jersey.
- Municipal (allowed_domains set to the town's site when it appears, else open search): "<town> planning board resolution <buyer>", "<buyer> PILOT agreement <town>", "<buyer> redevelopment agreement New Jersey", "<buyer> site plan application LLC New Jersey".
- Registries: "<entity name> opencorporates", "<entity name> New Jersey business entity", "<entity name> Delaware LLC" - record only what the excerpt shows.
- People: "<buyer> vice president signed", "<buyer> authorized signatory", "<buyer> managing member", "<buyer> principal New Jersey industrial" - only names that appear with the entity.
Target 8-20 entity rows per buyer where they exist; at least the manager/GP entity with address for every buyer. Use the known-deal context lines to seed town-specific searches.`

const SCHEMA = {
  type: 'object',
  properties: {
    part_file: { type: 'string' },
    rows_written: { type: 'integer' },
    buyers_covered: { type: 'array', items: { type: 'string' } },
    entities_per_buyer: { type: 'array', items: { type: 'object', properties: { buyer: { type: 'string' }, count: { type: 'integer' } }, required: ['buyer', 'count'] } },
    searches_run: { type: 'integer' },
    blocked: { type: 'array', items: { type: 'string' } },
    not_found: { type: 'array', items: { type: 'string' } },
    notes: { type: 'string' },
  },
  required: ['part_file', 'rows_written', 'buyers_covered', 'entities_per_buyer', 'searches_run', 'blocked', 'not_found', 'notes'],
}

// args.batches = [{ key: 'C_01', buyers: [{ name, type, context }] }, ...]
const BATCHES = (args && args.batches) || []
if (!BATCHES.length) throw new Error('args.batches required')

function promptForBase(b) {
  const path = '/home/user/cladue/buyers_research/parts/C_entities/' + b.key + '.jsonl'
  const list = b.buyers.map((x, i) => `${i + 1}. ${x.name}${x.type ? ' [' + x.type + ']' : ''}${x.context ? ' - known NJ deals/context: ' + x.context : ''}`).join('\n')
  return RULES + '\n\n' + TASK + '\n\nBUYERS IN THIS BATCH:\n' + list + '\n\nOUTPUT FILE (absolute path, JSONL): ' + path +
    '\n\nWhen done, return the structured summary: part_file, rows_written, buyers_covered, entities_per_buyer, searches_run, blocked, not_found (buyers with no sourced entity beyond the operating company), notes.'
}


// --- budget / continuation block appended to every agent prompt (args.search_cap, args.leads[key]) ---
function extra(key) {
  const cap = (args && args.search_cap) || 25
  const leads = (args && args.leads && args.leads[key]) || ''
  return '\n\nSEARCH BUDGET: you may run AT MOST ' + cap + ' WebSearch calls in total - count them. The pool is shared by every agent in this turn and exceeding your share starves the others. Plan your full query list first, run the highest-value queries first, and stop when you reach the cap or when WebSearch replies that the budget is used up - then Write your file immediately.' +
    '\n\nCONTINUING PRIOR WORK: if the output file already exists, Read it first and keep every existing row (correct only obvious errors); your final Write must contain the union of existing and new rows, deduped. Do not re-search items that already have complete rows unless they appear in the leads below.' +
    (leads ? '\n\nLEADS / GAPS FROM THE PREVIOUS PASS (start with these): ' + leads : '')
}
function promptFor(x) { return promptForBase(x) + extra(x.key) }

phase('Entities')
log('Workstream C: ' + BATCHES.length + ' batches, ' + BATCHES.reduce((n, b) => n + b.buyers.length, 0) + ' buyers')
const results = await parallel(BATCHES.map(b => () => agent(promptFor(b), { label: 'C:' + b.key, phase: 'Entities', schema: SCHEMA })))
const out = results.filter(Boolean)
log('C done: ' + out.reduce((n, r) => n + (r.rows_written || 0), 0) + ' entity rows across ' + out.length + ' parts')
return out
