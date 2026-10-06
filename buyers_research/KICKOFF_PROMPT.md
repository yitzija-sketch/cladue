# Paste this as the first message of the new session (branch `claude/nj-industrial-buyer-research-v4j2sy`)

```
Continue the NJ industrial buyer research in buyers_research/. Start by reading, in this order:
buyers_research/TASK_SPEC.md (the brief and rules), buyers_research/RESUME.md (state + how to resume),
buyers_research/TURN_PLAN.md (remaining batches), buyers_research/RESEARCH_LOG.md, and
buyers_research/parts/_runs/LEADS.json (gaps reported by the previous agents).

Environment: CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION has been raised, so the 200-searches-per-turn cap
should no longer apply - confirm with `echo $CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` and by running a
few WebSearch calls; if the cap is still 200 per turn, fall back to the batch sizes in TURN_PLAN.md.
Check whether WebFetch is still blocked (try https://re-nj.com/ and https://www.sec.gov/); if it now
works, tell the research agents they may fetch pages (criteria pages, 10-K Schedule III tables) directly.

Then run the remaining work with the Workflow tool using the scripts in buyers_research/tools/workflows/
(each takes args.{groups|slices|batches|targets}, args.search_cap, args.leads). With a lifted cap, you can
run whole workstreams at once (search_cap 60-80 per agent): batches 1-4 first (empty A groups, all B
slices, D3-D6), then A-expansion + C entities for the top-100 of buyer_activity_rank.csv, then
verification, then the 25 dossiers, then README.md + final RESEARCH_LOG.md + summary. After every
workflow: python3 -I buyers_research/tools/leads_from_journals.py && python3 -I buyers_research/tools/consolidate.py,
update RESEARCH_LOG.md sections 2-4 and TURN_PLAN.md statuses, commit and push to
claude/nj-industrial-buyer-research-v4j2sy. Start `bash buyers_research/tools/checkpoint.sh 600` in the
background (after editing its SESS path to the new session's transcript directory) so progress is pushed
every 10 minutes. Never modify anything outside buyers_research/ and NOTICE_buyers_research.md.
Agents must use only public free sources, never contact anyone, and leave unsourced cells blank.
```
