## What was asked and what was delivered

The brief asked for the public-web half of a NJ industrial buyer map: who is actively buying industrial
property in the 11 North/Central NJ counties, what they say they want, what they bought 2019–2024, and
which LLCs they buy through — structured to join to the broker's local tax-roll / entity graph on
`name_key`. Four CSV tables, 25 one-page dossiers, market statistics, a column dictionary and a research
log were delivered (counts in the tables above). Every row carries a public source URL; nothing was
guessed; nobody was contacted; no logins, paywalls or CAPTCHAs were used.

## How to read the activity ranking

"Press deal rows" counts distinct 2019–2024 property purchases found in trade press, brokerage releases
and SEC filings; "NJ deals seen (A)" is what the buy-box researcher saw while profiling the buyer
(including 2025–26 deals, which were deliberately not recorded as deal rows). Both undercount: most
sub-$5M trades are never reported, and the broker's tax-roll data is the authoritative count. The six
buyers on the broker's existing Elizabeth-port call list (CenterPoint, Terreno, Cabot, Sitex, Elberon,
Kurv/Bridge Industrial) were researched only lightly by instruction and are excluded from the top-25 and
the dossiers even though Sitex (14 rows), Prologis-scale CenterPoint (9) and Terreno (8) would otherwise
rank in the top ten.

## Buyer types on which the public web says little

* **Family offices and private 1031 buyers** — only 5 rows typed "family office"; ~40 private
  individuals / single-asset LLCs have a deal row and nothing else (no criteria, no sponsor page). The
  tax-roll graph, not the web, is the way to find and size these. The few repeat private buyers that do
  surface (Davco Group, STRO/Millstein, Legacy Real Estate Developers + Commerce Park Investors,
  Brentwood Realty/Opper, Treetop, Western Building, River Walk LLC, Devli) are worth a call list of their own.
* **Owner-users** — 70 rows, 1 with anything resembling criteria (by nature). The value is in the
  expansion signals in `notes` (Dora's Naturals, Deko International, Transcontinental Steel, Nest
  Scientific, Glendale Warehouse, Bay Crane, F.W. Webb) rather than buy boxes.
* **Foreign capital in sub-250K SF product** — Korean, German and Japanese investors appear only in
  big-box build-to-suit or portfolio deals; Mapletree (Westampton, Manalapan), Investcorp (one 44K SF
  building in a national portfolio), GIC/La Caisse/ADIA/CPP/PSP only as JV capital behind operators.
* **Non-traded REITs and DST sponsors** — strategy language is abundant (prospectuses), but NJ-specific
  holdings are rarely disclosed below the portfolio level; INREIT (152 Ridge Rd), PGIM PREF (1735 Jersey
  Ave), AIREIT (Wayne, 16-building NJ portfolio), JPMREIT (IOS) and Four Springs/Pilothouse (Belmar HQ)
  are the exceptions. No DST sponsor's NJ industrial asset surfaced.
* **Cap rates at the deal level** — press almost never prints them (two deal rows carry one; market
  reports give 12 cap-rate rows, mid-5% in 2024 and low-3% at the 2021 peak). Small-bay cap rates
  specifically are absent from the public record.
* **Acquisitions heads at the big open-end funds** — Invesco, PGIM, Principal, LaSalle, EQT Exeter,
  GLP/GCP, Nuveen rarely name a NJ or Northeast acquisitions lead; names were found for 56 of 377 buyers.
* **HQ street addresses** — the environment could not open firm websites, so most HQ cells carry
  city/state only; the entity table's c/o addresses (Form D / ADV) are the better join key anyway.

## Ten questions the data raised (for the broker to take to the local graph or a first call)

1. **How many "reported" deals are really in-window?** Of the undated press deals that were re-checked,
   roughly a third turned out to be 2017–2018 or 2025–2026 (Prologis Exit 8A $197M, Goodman Newark $360M,
   Terreno 130 Interstate $144M, Broadstone Perth Amboy, Crow/BGO Franklin, Fujipoly Edison, Kurv
   Carlstadt...). The remaining undated rows should be dated by the tax-roll last-sale date on join before
   anyone quotes them.
2. **Who is Devli, really?** The most active private buyer found (12+ Meadowlands/Bergen buys, incl.
   2026 Leonia and Upper Saddle River) is called "Wallington-based" by the press but lists 800 Ave at Port
   Imperial, Weehawken as HQ; Mark Devli (CIO) and Chris Devli (COO) are the only names; capital source and
   SPV names are undisclosed, and Deugen Investment Group is a separate Hoboken firm that co-invested once.
3. **Do the SPV naming patterns hold in the registry?** Seagis `SPG <Town> LLC`, Cohen Asset
   Management `<Town> SPE LLC`, Ares `BCI IV / AIREIT <property> DC LLC`, Dermody `DPIF <state> <n>
   <project> LLC`, Faropoint `FRG-X-NJ<n> LP`, Denholtz `DENHOLTZ <address> LLC`, Forsgate `Forsgate
   Ventures <roman> LLC`, Prologis `Prologis-Exchange <address> LLC`, Taurus `TCD 257 SNJ ...` — each is
   evidenced by one to four named entities; the local registry/mailing-address clustering can confirm or
   kill each pattern in minutes.
4. **Which c/o mailing addresses sit on the most NJ tax bills?** Faropoint 111 River St Ste 1010
   Hoboken; Realterm 201 West St Annapolis; Sagard/EverWest 1099 18th St Denver; Dermody 5500 Equity Ave
   Reno; CBRE IM 200 Park Ave Ste 2001 NY; Sitex 10 W Forest Ave Englewood; Seagis 100 Front St
   Conshohocken; Penwood (Fund VI); Taurus c/o 4 Radnor Corp Center; Brookfield 250 Vesey St 15th Fl;
   BGO 399 Park Ave 18th Fl; Invesco 2001 Ross Ave Dallas. Matching these to the tax roll turns ~45 buyers
   with no public SPV name into holdings lists.
5. **Faropoint's box has moved — where is it now?** Stated 20K–100K SF (site) vs 20K–200K SF with
   ~10-year leases (ROI-NJ), Invesco minority stake since 2023, 2025 Florham Park $9.25M, $144.5M
   Allendale/Mahwah 2023: are they still buying single-tenant sub-50K SF boxes in 2026, and through
   which FRG-X vehicle?
6. **How much IOS capital is still un-deployed in NJ?** Ambient $156M Harrison/Kearny (2024), Realterm
   $277M 13-property buy from Brookfield (2024-12), Sagard/La Caisse US$360M JV (2026), Dalfen/Centerbridge,
   Ridgecut Road (5+ buys 2024–26), Jadian, Alterra, Catalyst, Outpost — against pricing of $8–10K/acre/
   month rent (Fennelly) and up to ~$7M/acre (Moonachie). Which of these will pay for 2–5-acre infill yards
   under $10M?
7. **Why so few sale-leasebacks?** Only ~10 NJ industrial SLBs surfaced 2019–2024 (Unifoil/EverWest,
   Diamond Chemical/EverWest, Kiss→Duke, Bed Bath & Beyond/Oak Street, RAB/Suburban Jersey, Allstate Can/
   Longpoint...). With Oak Street, W. P. Carey ($5–500M), Four Springs ($5–25M, Belmar), Mesirow (>$10M),
   LCN and AG Net Lease all stating appetite, which NJ owner-occupiers in the broker's graph fit?
8. **Who are the net sellers of 2025–26?** Plymouth sold its only NJ asset; First Industrial sold
   Montville to Longpoint; Hampshire/Invesco flipped 333 North St Teterboro to Principal for +$40M in two
   years; MSREI sold Eastpoint at 8A to Property Reserve; Goldman/Dalfen sold Roxbury to ICE; Woodmont sold
   to Sagard; Blackstone sold to Prologis and to Nuveen. Are these programmatic exits the broker can get
   ahead of?
9. **What do the merchant-build JVs want next?** Trammell Crow/CBRE IM (Sayreville), Hampshire/Invesco
   (Bogota, Teterboro), Woodmont/Sagard (Rahway, Woodbridge), Russo/Forsgate (Kingsland 718 ac), Lincoln
   Equities/PGIM, Greek/Hampshire (Parsippany), Altman/DWS (Hamilton), Deugen/Faropoint (New Brunswick),
   Crow Holdings — all bought land or obsolete buildings 2019–24. Which corridors are they still
   underwriting at 2026 rents?
10. **Is the sub-250K SF market still institutional?** 360 of the dated deals under 250K SF show a mix
    of Faropoint, Longpoint, Camber, Cohen, Seagis, Devli, STRO, Oliver Street/Bain, NorthBridge, Taurus,
    High Street ($3–250M, 24' clear, post-1980) against a growing owner-user and 1031 cohort as prices
    reset from $200+/SF (2022) to $180–190/SF (2024–25, NAI). Who is still paying the institutional price
    for 30–100K SF multi-tenant buildings in 2026?

## Caveats that travel with every number

* **Search-excerpt based.** This cloud environment blocked direct page fetches; all facts came from web-
  search excerpts of pages (including SEC filings, PDFs and article text). Verification sampled ~10% of
  rows against the cited domain plus an independent source and found a 3–4% refutation rate, almost
  all dates. Undated rows have an estimated one-third chance of being outside 2019–2024.
* **The repo's `cloud_context/` folder was absent**, so "already known locally" could not be excluded
  precisely; the brief's own exclusions were applied (no 2025–26 press deals as rows; call-list buyers
  light). Expect overlap with the local graph — the join will show it.
* **Email patterns and phones** were recorded only when seen on a real public address (2 and 8 rows).
* **The research paused 2026-10-06 → 10-11** when usage credits lapsed; nothing was lost (every agent's
  output is committed, and two interrupted agents resumed from their half-written files).
