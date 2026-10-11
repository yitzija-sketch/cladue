export const meta = {
  name: 'nj-dossiers-E',
  description: 'Workstream E: one-page broker dossiers for the most active NJ industrial buyers, built from the consolidated CSVs plus a few gap-filling searches',
  phases: [{ title: 'Dossiers', detail: 'one agent per buyer; writes buyers_research/dossier_<slug>.md' }],
}

const RULES = `You are writing a ONE-PAGE broker dossier on an active buyer of New Jersey industrial real estate, for a tenant-rep / investment-sales broker preparing a first call. Audience: a broker, not an analyst. Plain language, specific facts, every fact sourced.

INPUTS: First Read your context pack (path given below): it holds the buyer's row from buyers_stated.csv (stated criteria, people, confidence), its 2019-2024 NJ deal rows, its entity rows (SPVs / funds / managers with addresses) and any market-report mentions. That pack is your primary source - most of the dossier must come from it. Then run AT MOST the number of WebSearch calls stated below (load WebSearch with ToolSearch "select:WebSearch" if needed; WebFetch/curl are blocked) to fill the biggest gaps only: (a) the buyer's most recent NJ activity 2025-2026 and any stated change of strategy, (b) the acquisitions lead for NJ/Northeast if the pack lacks one, (c) typical check size if the pack lacks prices. Use mode "extended" for firm-specific queries; use allowed_domains for the firm's own site and for roi-nj.com / re-nj.com / njbiz.com.

RULES: Public free sources only; never contact anyone. Do not invent facts, people, emails or phone numbers - if something is unknown, write "not found in public sources". Every factual sentence that is not from the context pack carries a source URL in parentheses; facts from the pack cite the pack's source_url / evidence_url. Do not give investment advice; describe what the buyer does and what it says it wants. Keep to roughly one page (450-700 words). Dates as YYYY-MM or YYYY. Money as $12.5M.

FORMAT (Markdown, exactly these sections, in this order):
# <Buyer name> - NJ industrial buyer dossier
*Prepared <today's date> from buyers_research (A/B/C files) + <n> gap-filling searches. Confidence: <high|med|low> overall.*

## 1. Who they are and what they do in NJ
3-5 sentences: type (REIT / fund / developer-holder / IOS specialist / owner-user ...), parent and capital source, HQ and NJ office, how long active in NJ, what product and submarkets they actually buy (from the deal rows), hold strategy.

## 2. Stated buy box
Bullet list of the stated criteria from the A row (size, price, product, submarkets, tenancy, structures, clear height / age) with the quote and its source URL; say "no published criteria - pattern inferred from deals:" when the A row has none and then give the inferred pattern clearly labelled as inferred.

## 3. Last NJ acquisitions (2019-2024, newest first)
Table: | Date | Address, Town | SF / acres | Price | Type | Seller / notes | Source |  - 5 to 10 rows from the deal rows; if fewer than 5 exist say so. Add a one-line note on 2025-2026 activity from your searches if found.

## 4. Typical check size and deal shape
2-4 sentences: price range and SF range of the deals above (compute from the rows), single-asset vs portfolio, all-cash / JV / sale-leaseback, speed signals (e.g. closed off-market, 1031).

## 5. Entities they buy through
Bullet list of SPV naming patterns, fund vehicles, manager/GP and the mailing / c/o address the broker should expect on a tax bill, each with its evidence type and confidence; say which are INFERRED.

## 6. Key people
Acquisitions head / regional lead and 1-3 other named decision-makers with titles and the URL where the name appeared. No personal contact details.

## 7. What would make a property match them
4-6 bullets translating the above into a screen the broker can apply (size band, submarket, tenancy, physical specs, price band, timing).

## 8. Five questions for the first call
Exactly 5 numbered, specific questions that surface what the public record cannot (current fund's dry powder and hold period, appetite for vacancy / IOS / cold, 2026 target submarkets, decision process and timeline, who sources deals for them).

## Sources
Deduplicated list of every URL cited.

OUTPUT: Write the file to the exact absolute path given below using the Write tool, then return the structured summary. Your final answer is the structured output only.`

const SCHEMA = {
  type: 'object',
  properties: {
    file: { type: 'string' },
    buyer: { type: 'string' },
    sections_with_gaps: { type: 'array', items: { type: 'string' } },
    searches_run: { type: 'integer' },
    new_facts_from_search: { type: 'array', items: { type: 'string' } },
    overall_confidence: { type: 'string', enum: ['high', 'med', 'low'] },
  },
  required: ['file', 'buyer', 'sections_with_gaps', 'searches_run', 'new_facts_from_search', 'overall_confidence'],
}

let TARGETS = (args && args.targets) || []
if (!TARGETS.length && args && args.target_keys) TARGETS = args.target_keys.map(k => ({ key: k }))
if (!TARGETS.length) throw new Error('args.targets or args.target_keys required')
const CAP = (args && args.search_cap) || 7
const TODAY = (args && args.today) || '2026-10-11'

function promptFor(t) {
  const lookup = t.context_file
    ? `CONTEXT PACK: ${t.context_file}. BUYER: ${t.name}. OUTPUT FILE: /home/user/cladue/buyers_research/dossier_${t.slug}.md.`
    : `FIRST, Read /home/user/cladue/buyers_research/parts/_runs/E_TARGETS.json and take the object whose key is "${t.key}": its context_file is your CONTEXT PACK, its name is the BUYER, and your OUTPUT FILE is /home/user/cladue/buyers_research/dossier_<its slug>.md.`
  return RULES + `\n\n${lookup}\nToday's date: ${TODAY}. SEARCH CAP: at most ${CAP} WebSearch calls (hard limit; count them).` +
    '\n\nWhen done, return: file, buyer, sections_with_gaps (section numbers where public sources were thin), searches_run, new_facts_from_search (one line each, with URL), overall_confidence.'
}

phase('Dossiers')
log('Workstream E: ' + TARGETS.length + ' dossiers, cap ' + CAP + ' searches each')
const results = await parallel(TARGETS.map(t => () => agent(promptFor(t), { label: 'E:' + t.key, phase: 'Dossiers', schema: SCHEMA })))
const out = results.filter(Boolean)
log('E done: ' + out.length + ' dossiers written')
return out
